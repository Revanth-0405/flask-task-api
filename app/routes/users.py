from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.models.user import User
from app.extensions import db
from app.utils.decorators import auth_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/<string:user_id>', methods=['GET'])
@auth_required()
def get_user(user_id):
    current_user = get_jwt_identity()
    if current_user != user_id:
        return jsonify({"error": True, "message": "Unauthorized"}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200

@users_bp.route('/<string:user_id>', methods=['PUT', 'PATCH'])
@auth_required()
def update_user(user_id):
    current_user = get_jwt_identity()
    if current_user != user_id:
        return jsonify({"error": True, "message": "Unauthorized"}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'username' in data: user.username = data['username']
    if 'email' in data: user.email = data['email']
    
    db.session.commit()
    return jsonify(user.to_dict()), 200

@users_bp.route('/<string:user_id>', methods=['DELETE'])
@auth_required()
def delete_user(user_id):
    current_user = get_jwt_identity()
    if current_user != user_id:
        return jsonify({"error": True, "message": "Unauthorized"}), 403
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200