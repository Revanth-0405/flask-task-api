from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import User
from werkzeug.security import generate_password_hash

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
def get_users():
    # Only fetch users that are not soft-deleted
    users = User.query.filter_by(is_deleted=False).all()
    return jsonify([user.to_dict() for user in users]), 200

@users_bp.route('/<id>', methods=['GET'])
def get_user(id):
    user = User.query.filter_by(id=id, is_deleted=False).first_or_404()
    return jsonify(user.to_dict()), 200

@users_bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json()
    
    # Hash the password before saving
    hashed_password = generate_password_hash(data['password'])
    
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created", "id": new_user.id}), 201

@users_bp.route('/<id>', methods=['PUT'])
def update_user(id):
    user = User.query.filter_by(id=id, is_deleted=False).first_or_404()
    data = request.get_json()
    
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
        
    db.session.commit()
    return jsonify({"message": "User updated", "user": user.to_dict()}), 200

@users_bp.route('/<id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.filter_by(id=id, is_deleted=False).first_or_404()
    
    # Soft delete logic
    user.is_deleted = True
    db.session.commit()
    
    return jsonify({"message": "User softly deleted"}), 200