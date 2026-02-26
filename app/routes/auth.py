from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity, create_access_token
from app.services.auth_service import AuthService
from app.schemas.user_schema import UserCreateSchema
from app.utils.decorators import auth_required

auth_bp = Blueprint('auth', __name__)
user_schema = UserCreateSchema()

# 1. POST /api/auth/register
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    errors = user_schema.validate(data)
    if errors:
        return jsonify({"error": True, "message": "Validation Error", "details": errors}), 400
    
    response, status = AuthService.register_user(data)
    return jsonify(response), status

# 2. POST /api/auth/login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    response, status = AuthService.login_user(data)
    return jsonify(response), status

# 3. POST /api/auth/refresh
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify(access_token=new_access_token), 200

# 4. POST /api/auth/logout
@auth_bp.route('/logout', methods=['POST'])
@auth_required()
def logout():
    jti = get_jwt()["jti"]
    response, status = AuthService.logout_user(jti)
    return jsonify(response), status