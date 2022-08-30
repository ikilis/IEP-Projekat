from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request

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
