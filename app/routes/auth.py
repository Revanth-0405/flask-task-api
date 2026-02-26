from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.user import User
from app.schemas.user_schema import UserCreateSchema, UserUpdateSchema

# We will prefix this blueprint with /api/users in __init__.py
users_bp = Blueprint('users', __name__)
create_schema = UserCreateSchema()
update_schema = UserUpdateSchema()

# POST /api/users (Create user)
@users_bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json()
    
    # Fix 2.1: Validate input before accessing fields
    errors = create_schema.validate(data)
    if errors:
        return jsonify({"error": True, "message": "Validation failed", "details": errors}), 400

    new_user = User(username=data['username'], email=data['email'])
    new_user.set_password(data['password'])

    # Fix 2.2: Explicitly handle duplicate users
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": True, "message": "Username or email already exists"}), 409

# GET /api/users (List all users)
@users_bp.route('/', methods=['GET'])
def get_users():
    users = User.query.filter_by(is_active=True).all()
    return jsonify([user.to_dict() for user in users]), 200

# GET /api/users/<id> (Get single user)
@users_bp.route('/<id>', methods=['GET'])
def get_user(id):
    user = User.query.filter_by(id=id, is_active=True).first()
    if not user:
        return jsonify({"error": True, "message": "User not found"}), 404
    return jsonify(user.to_dict()), 200

# PUT /api/users/<id> (Update user)
@users_bp.route('/<id>', methods=['PUT'])
def update_user(id):
    user = User.query.filter_by(id=id, is_active=True).first()
    if not user:
        return jsonify({"error": True, "message": "User not found"}), 404

    data = request.get_json()
    errors = update_schema.validate(data)
    if errors:
        return jsonify({"error": True, "message": "Validation failed", "details": errors}), 400

    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']

    try:
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": True, "message": "Username or email already exists"}), 409

# DELETE /api/users/<id> (Soft delete user)
@users_bp.route('/<id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.filter_by(id=id, is_active=True).first()
    if not user:
        return jsonify({"error": True, "message": "User not found"}), 404

    user.is_active = False # Soft delete
    db.session.commit()
    return jsonify({"message": "User soft deleted successfully"}), 200