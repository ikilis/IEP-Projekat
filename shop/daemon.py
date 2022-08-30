import json
from functools import wraps

from flask import Flask, request, Response, jsonify
from redis import Redis

from configuration import Configuration
from models import database, Product, Category, ProductCategory, Order, ProductOrder
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity, verify_jwt_in_request
from sqlalchemy import and_
import re

if __name__ == "__main__":
    application = Flask(__name__)
    application.config.from_object(Configuration)
    database.init_app(application)
    while True:
        with Redis(host=Configuration.REDIS_HOST) as redis:
            with application.app_context() as context:
                    read_bytes = redis.blpop(Configuration.REDIS_PRODUCT_LIST)
                    product = json.loads(read_bytes[1])
                    categories = product["categories"].split("|")
                    existingProduct = Product.query.filter(Product.name == product["name"]).first()
                    # nov proizvod
                    if not existingProduct:
                        newProduct = Product(name=product["name"], price=product["price"], quantity=product["quantity"])
                        database.session.add(newProduct)
                        database.session.commit()
                        for category in categories:
                            existingCategory = Category.query.filter(Category.name == category).first()
                            if not existingCategory:
                                newCategory = Category(name=category)
                                database.session.add(newCategory)
                                database.session.commit()
                                pc = ProductCategory(productId=newProduct.id, categoryId=newCategory.id)
                            else:
                                pc = ProductCategory(productId=newProduct.id, categoryId=existingCategory.id)
                            database.session.add(pc)
                            database.session.commit()
                    # vec postoji u bazi, proveri mu kategorije
                    else:
                        bad = False
                        # cao = product.categories
                        for category in categories:
                            if any(cat.name == category for cat in existingProduct.categories):
                                continue
                            bad = True
                            break
                        if bad:
                            continue
                        newPrice = (existingProduct.quantity * existingProduct.price + product["price"] * product[
                            "quantity"])
                        newPrice = newPrice / float(existingProduct.quantity + product["quantity"])
                        existingProduct.price = newPrice
                        existingProduct.quantity += product["quantity"]
                        tmp_quantity = existingProduct.quantity
                        database.session.commit()

                        # bez dohvatanja (.all/.first) jer menjanje baze  ponistava kverije
                        orders = Order.query.filter(Order.status == "PENDING").join(ProductOrder).join(Product).filter(
                            Product.name == existingProduct.name).group_by(Order.id).order_by(Order.timestamp)

                        for order in orders:
                            existingProduct = Product.query.filter(Product.name == product["name"]).first()

                            if existingProduct.quantity == 0:
                                break

                            orderedProds = ProductOrder.query.filter(
                                and_(
                                    ProductOrder.orderId == order.id,
                                    ProductOrder.productId == existingProduct.id
                                )
                            )

                            for prod in orderedProds:
                                existingProduct = Product.query.filter(Product.name == product["name"]).first()
                                if existingProduct.quantity == 0:
                                    break

                                if existingProduct.quantity >= prod.requested - prod.received:
                                    existingProduct.quantity -= (prod.requested - prod.received)
                                    prod.received = prod.requested
                                    database.session.commit()
                                else:
                                    prod.received += existingProduct.quantity
                                    existingProduct.quantity = 0
                                    database.session.commit()

                            remaining = ProductOrder.query.filter(
                                and_(
                                    ProductOrder.orderId == order.id,
                                    ProductOrder.received != ProductOrder.requested
                                )
                            ).first()

                            if not remaining:
                                order.status = "COMPLETE"
                                database.session.commit()

