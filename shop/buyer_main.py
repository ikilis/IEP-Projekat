from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, Category, Product, ProductCategory, Order, ProductOrder
from flask_jwt_extended import JWTManager, jwt_required, get_jwt, \
    get_jwt_identity, verify_jwt_in_request
from sqlalchemy import and_
from decorator import role_decorator
from datetime import datetime

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

def isInt(str):
    try:
        int(str)
    except ValueError:
        return False
    return int(str)>0

@application.route("/search", methods=["GET"])
@role_decorator(role="kupac")
def search():
    prod = request.args.get("name", None)
    cat = request.args.get("category", None)

    if cat and prod:
        categories = Category.query.join(ProductCategory).join(Product).filter(
            and_(*[
                 Product.name.like(f"%{prod}%"),
                 Category.name.like(f"%{cat}%")
                 ]
                 )
        ).group_by(Category.id).with_entities(Category.name).all()
        products = Product.query.join(ProductCategory).join(Category).filter(
               and_(
                   *[
                       Product.name.like(f"%{prod}%"),
                       Category.name.like(f"%{cat}%")
                   ]
                )
            ).group_by(Product.id).all()
    elif prod:
        categories = Category.query.join(ProductCategory).join(Product).filter(
                and_(
                    *[
                        Product.name.like(f"%{prod}%")
                    ]
                )
            ).group_by(Category.id).with_entities(Category.name).all()
        products = Product.query.filter(Product.name.like(f"%{prod}%")).all()
    elif cat:
        categories = Category.query.filter(Category.name.like(f"%{cat}%")).with_entities(Category.name).all()
        products = Product.query.join(ProductCategory).join(Category).filter(
                *[
                    Category.name.like(f"%{cat}%")
                ]
            ).all()
    else:
        categories = Category.query.with_entities(Category.name).all()
        products = Product.query.all()

    ret_product = []
    for product in products:
        myCategories = []
        for pc in product.categories:
            myCategories.append(pc.name)
        ret_product.append({
            "categories": myCategories,
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "quantity": product.quantity
        })
    ret_category = []
    for category in categories:
        ret_category.append(category[0])

    return jsonify(categories=ret_category, products=ret_product)


@application.route("/order", methods=["POST"])
@role_decorator(role="kupac")
def order():
    requests = request.json.get("requests", None)
    if not requests:
        return jsonify(message="Field requests is missing."), 400

    quantities = []
    products = []
    prices = []
    totalPrice = 0
    rowCnt = 0
    for req in requests:
        id = req.get("id", "")
        if id == "":
            return jsonify(message=f"Product id is missing for request number {rowCnt}."), 400
        quantity = req.get("quantity", "")
        if quantity == "":
            return jsonify(message=f"Product quantity is missing for request number {rowCnt}."), 400
        if not isInt(id) or (isInt(id) < 0):
            return jsonify(message=f"Invalid product id for request number {rowCnt}."), 400
        if not isInt(quantity):
            return jsonify(message=f"Invalid product quantity for request number {rowCnt}."), 400
        product = Product.query.filter(Product.id == id).first()
        if not product:
            return jsonify(message=f"Invalid product for request number {rowCnt}."), 400
        rowCnt += 1

        products.append(product.id)
        quantities.append(quantity)
        # mozda ne treba da mnozim ovde
        price = product.price * quantity
        prices.append(product.price)
        totalPrice += price

    claims = get_jwt()
    email = claims["email"]

    newOrder = Order(price=totalPrice, customer=email, status="TBD", timestamp=datetime.today())
    database.session.add(newOrder)
    database.session.commit()

    pending = False
    for pp_id, qq, pr in zip(products, quantities, prices):
        pp = Product.query.filter(Product.id == pp_id).first()
        product_order = ProductOrder(productId=pp.id, orderId=newOrder.id, requested=qq, price=pr)
        delivered = 0
        if pp.quantity >= qq:
            pp.quantity -= qq
            delivered = qq
        else:
            delivered = pp.quantity
            pp.quantity = 0
            pending = True
        product_order.received = delivered
        database.session.add(product_order)
        # database.session.add(pp)
        database.session.commit()

    if pending:
        newOrder.status = "PENDING"
    else:
        newOrder.status = "COMPLETE"
    # database.session.add(newOrder)
    database.session.commit()

    return jsonify(id=newOrder.id), 200

@application.route("/status", methods=["GET"])
@role_decorator(role="kupac")
def status():
    claims = get_jwt()
    email = claims["email"]

    ret = []

    myOrders = Order.query.filter(Order.customer == email).all()
    for order in myOrders:
        orderedProducts = ProductOrder.query.filter(ProductOrder.orderId == order.id).all()
        tmp_products = []
        for product in orderedProducts:
            name = Product.query.filter(Product.id == product.productId).first().name
            prod_categories = ProductCategory.query.filter(ProductCategory.productId == product.productId).all()
            productCategories = []
            for pc in prod_categories:
                productCategories.append(Category.query.filter(Category.id == pc.categoryId).first().name)
            tmp_products.append({

                "categories": productCategories,
                "name": name,
                "price": product.price,
                "received": product.received,
                "requested": product.requested
            })
        ret.append({
            "products": tmp_products,
            "price": order.price,
            "status": order.status,
            "timestamp": order.timestamp
        })
    return jsonify(orders=ret), 200


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5004)


