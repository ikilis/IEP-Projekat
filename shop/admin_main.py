import json

from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, Category, ProductCategory, Product, ProductOrder
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity, verify_jwt_in_request
from sqlalchemy import func
import re
from decorator import role_decorator

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/", methods=["GET"])
# @role_decorator(role="admin")
def index_ruta():
    # testCategory = Category(name="Test Kategorija")
    # database.session.add(testCategory)
    # database.session.commit()

    return str(Category.query.all())

@application.route("/categoryStatistics", methods=["GET"])
@role_decorator(role="admin")
def category_statistics():

    categories = Category.query.outerjoin(ProductCategory).outerjoin(Product).outerjoin(ProductOrder)\
                .group_by(Category.id).order_by(func.sum(ProductOrder.requested).desc()).order_by(Category.name)

    ret = []
    for category in categories:
        ret.append(category.name)

    return jsonify(statistics=ret)

@application.route("/productStatistics", methods=["GET"])
@role_decorator(role="admin")
def product_statistics():
    products = Product.query.all()
    ret = []

    for product in products:
        productOrders = ProductOrder.query.filter(ProductOrder.productId == product.id).all()
        if not productOrders:
            continue
        sold = 0
        waiting = 0
        for order in productOrders:
            waiting = waiting + order.requested - order.received
            sold = sold + order.requested
        ret.append({"name": product.name, "sold": sold, "waiting": waiting})

    return jsonify(statistics=ret), 200


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5001)