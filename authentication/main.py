from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, User
import re   # regex
from sqlalchemy import and_
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token,\
        jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from functools import wraps


application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)

def role_decorator(role):
    def inner(function):
        @wraps(function)
        def decorator(*args, **keywordArgs):
            verify_jwt_in_request()
            additionalClaims = get_jwt()
            if additionalClaims["roles"] == role:
                return function(*args, **keywordArgs)
            else:
                return jsonify({
                "msg": "Missing Authorization Header"
            }), 401

        return decorator

    return inner


@application.route("/", methods=["GET"])
def index_ruta():
    return "Radi indeksna ruta, auth"

@application.route("/register", methods=["POST"])
def register():
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    isCustomer = request.json.get("isCustomer", "")

    if len(forename) == 0:
        return jsonify({
            "message": "Field forename is missing."
        }), 400
    if len(surname) == 0:
        return jsonify({
            "message": "Field surname is missing."
        }), 400
    if len(email) == 0:
        return jsonify({
            "message": "Field email is missing."
        }), 400
    if len(password) == 0:
        return jsonify({
            "message": "Field password is missing."
        }), 400
    if isCustomer == "":
        return jsonify({
            "message": "Field isCustomer is missing."
        }), 400

    if not re.fullmatch('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email):
        return jsonify({
            "message": "Invalid email."
        }), 400

    if len(password) < 8 or not re.search(r'[a-z]', password) or not re.search(r'[A-Z]', password) or not re.search(r'\d', password):
        return jsonify({
            "message": "Invalid password."
        }), 400


    if User.query.filter(User.email == email).first():
        return jsonify({
            "message": "Email already exists."
        }), 400

    role = "magacioner" if not isCustomer else "kupac"
    newUser = User(email=email, password=password, forename=forename, surname=surname, roles=role)

    database.session.add(newUser)
    database.session.commit()

    return Response(status=200)

@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    if email == "":
        return jsonify({
            "message": "Field email is missing."
        }), 400
    if password == "":
        return jsonify({
            "message": "Field password is missing."
        }), 400
    if not re.fullmatch('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email):
        return jsonify({
            "message": "Invalid email."
        }), 400

    loggedUser = User.query.filter(and_(User.email == email, User.password == password)).first()
    if not loggedUser:
        return jsonify({
            "message": "Invalid credentials."
        }), 400


    additionalClaims = {
        "email": loggedUser.email,
        "forename": loggedUser.forename,
        "surname": loggedUser.surname,
        "roles": loggedUser.roles
    }
    accessToken = create_access_token(identity=loggedUser.email, additional_claims=additionalClaims)
    refreshToken = create_refresh_token(identity=loggedUser.email, additional_claims=additionalClaims)

    return jsonify(accessToken=accessToken, refreshToken=refreshToken)



@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refreshClaims = get_jwt()

    additionalClaims = {
        "email": refreshClaims["email"],
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "roles": refreshClaims["roles"]
    }
    accessToken = create_access_token(identity=identity, additional_claims=additionalClaims)
    return jsonify(accessToken=create_access_token(identity=identity, additional_claims=additionalClaims)), 200

@application.route("/delete", methods=["POST"])
@role_decorator(role="admin")
def delete():
    email = request.json.get("email", "")

    if email == "":
        return jsonify({
            "message": "Field email is missing."
        }), 400

    if not re.fullmatch('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email):
        return jsonify({
            "message": "Invalid email."
        }), 400

    existingUser = User.query.filter(User.email == email).first()

    if not existingUser:
        return jsonify({
            "message": "Unknown user."
        }), 400

    database.session.delete(existingUser)
    database.session.commit()

    return Response(status=200)


if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
