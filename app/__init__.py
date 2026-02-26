from flask import Flask
from app.config import config_by_name
from app.extensions import db, migrate, ma

def create_app(config_name='dev'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    # Import models
    from app.models.user import User

    # Register blueprints exactly as requested in Section 4.2
    from app.routes.health import health_bp
    from app.routes.auth import users_bp
    
    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(users_bp, url_prefix='/api/users')

    return app