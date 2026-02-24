from flask import Flask
from app.config import config_by_name
from app.extensions import db, migrate

def create_app(config_name='dev'):
    """Flask Application Factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions with the app context
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes.health import health_bp
    from app.routes.users import users_bp
    
    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(users_bp, url_prefix='/api/users')

    return app