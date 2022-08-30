import csv
import io

from flask import Flask, request, jsonify
from configuration import Configuration
from models import database
from flask_jwt_extended import JWTManager
from decorator import role_decorator
from redis import Redis
import json

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

def isFloat(str):
    try:
        float(str)
    except ValueError:
        return False
    return float(str) > 0

def isInt(str):
    try:
        int(str)
    except ValueError:
        return False
    return int(str)>0

@application.route("/update", methods=["POST"])
@role_decorator(role="magacioner")
def update():
    input_file = request.files.get("file", None)
    if not input_file:
        return jsonify(message="Field file is missing."), 400

    content = input_file.stream.read().decode("utf-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)

    products = []
    rowCnt = 0
    for row in reader:
        if len(row) != 4:
            return jsonify(message=f"Incorrect number of values on line {rowCnt}."), 400
        if not isInt(row[2]):
            return jsonify(message=f"Incorrect quantity on line {rowCnt}."), 400
        if not isFloat(row[3]):
            return jsonify(message=f"Incorrect price on line {rowCnt}."), 400
        rowCnt += 1

        newProduct = {
            "categories": row[0],
            "name": row[1],
            "quantity": int(row[2]),
            "price": float(row[3])
        }
        products.append(newProduct)

    with Redis(host=Configuration.REDIS_HOST) as redis:
        for product in products:
            redis.rpush(Configuration.REDIS_PRODUCT_LIST, json.dumps(product))

    return "MAGACIONER"



if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5003)
