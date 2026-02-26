from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, create_refresh_token
from app.extensions import db
from app.models.user import User, TokenBlocklist

class AuthService:
    @staticmethod
    def register_user(data):
        new_user = User(username=data['username'], email=data['email'])
        new_user.set_password(data['password'])
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return {"error": False, "message": "User registered successfully", "user": new_user.to_dict()}, 201
        except IntegrityError:
            db.session.rollback()
            return {"error": True, "message": "Username or email already exists", "details": {}}, 409

    @staticmethod
    def login_user(data):
        user = User.query.filter_by(email=data.get('email'), is_active=True).first()
        if user and user.check_password(data.get('password')):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200
            
        return {"error": True, "message": "Invalid credentials", "details": {}}, 401

    @staticmethod
    def logout_user(jti):
        db.session.add(TokenBlocklist(jti=jti))
        db.session.commit()
        return {"message": "Successfully logged out"}, 200