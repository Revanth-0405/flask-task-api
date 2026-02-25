from flask import Flask
from app.config import config_by_name
from app.extensions import db, migrate, jwt, swagger

def create_app(config_name='dev'):
    """Flask Application Factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions with the app context
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    swagger.init_app(app)
    
    # Register blueprints
    from app.routes.health import health_bp
    from app.routes.users import users_bp
    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp
        
    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    
    @app.errorhandler(404)
    def not_found(e):
        return {"msg": "Resource not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return {"msg": "Internal server error"}, 500
    
    
    return app