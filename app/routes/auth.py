from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import User
from flask_jwt_extended import create_access_token
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    User Registration
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            username:
              type: string
              example: dev_user
            email:
              type: string
              example: dev@example.com
            password:
              type: string
              example: SecurePass123!
    responses:
      201:
        description: User registered successfully
      400:
        description: User already exists
    """
    data = request.get_json()
    
    # Check if user already exists
    if User.query.filter_by(username=data.get('username')).first() or \
       User.query.filter_by(email=data.get('email')).first():
        return jsonify({"msg": "User already exists"}), 400

    new_user = User(
        username=data.get('username'),
        email=data.get('email')
    )
    new_user.set_password(data.get('password'))
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"msg": "User registered successfully", "user_id": new_user.id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User Login
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            username:
              type: string
              example: dev_user
            password:
              type: string
              example: SecurePass123!
    responses:
      200:
        description: Returns a JWT access token
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()

    if user and user.check_password(data.get('password')):
        expires = datetime.timedelta(hours=24)
        # Ensure identity is a string for UUID compatibility
        access_token = create_access_token(identity=str(user.id), expires_delta=expires)
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Bad username or password"}), 401