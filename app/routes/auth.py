from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import User
from flask_jwt_extended import create_access_token
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if user already exists
    if User.query.filter_by(username=data.get('username')).first() or \
       User.query.filter_by(email=data.get('email')).first():
        return jsonify({"msg": "User already exists"}), 400

    new_user = User(
        username=data.get('username'),
        email=data.get('email')
    )
    # This uses the method we added in Phase 2 to hash the password
    new_user.set_password(data.get('password'))
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"msg": "User registered successfully", "user_id": new_user.id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()

    if user and user.check_password(data.get('password')):
        # Create a token that expires in 24 hours
        expires = datetime.timedelta(hours=24)
        access_token = create_access_token(identity=user.id, expires_delta=expires)
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Bad username or password"}), 401