from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError
from jwt.exceptions import ExpiredSignatureError

def auth_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception as e:
                return jsonify({
                    "error": True, 
                    "message": "Authentication failed or missing token", 
                    "details": str(e)
                }), 401
            return fn(*args, **kwargs)
        return decorator
    return wrapper