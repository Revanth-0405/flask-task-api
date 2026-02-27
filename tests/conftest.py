# tests/conftest.py
import pytest
from app import create_app
from app.extensions import db

@pytest.fixture
def app():
    # Create the app with a test configuration
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # Use an in-memory DB for fast tests
        "JWT_SECRET_KEY": "this-is-a-super-test-secret-test-key"
    })

    # Setup the database before the test, tear it down after
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(app):
    from flask_jwt_extended import create_access_token
    from app.extensions import db
    from app.models.user import User # Assuming this is the correct path to your User model
    
    with app.app_context():
        # 1. Create a fake user in the test database so the Foreign Key has something to point to
        test_user = User(
            id="1", # Use the same string ID here! If your user ID auto-generates as a UUID, you might need to grab that UUID instead.
            username="testuser",
            email="test@example.com",
            password_hash="fakehash" # Use whatever required fields your User model has
        )
        db.session.add(test_user)
        db.session.commit()

        # 2. Generate the token for that specific user
        token = create_access_token(identity=test_user.id) 
        return {"Authorization": f"Bearer {token}"}