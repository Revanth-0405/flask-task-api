from flask import Flask
from app.config import config_by_name
from app.extensions import db, migrate, ma, jwt
from app.utils.error_handlers import register_error_handlers, setup_logging # ADDED: setup_logging

def create_app(config_name='dev'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)

    # Import models
    from app.models.user import User, TokenBlocklist
    from app.models.task import Task

    #JWT blacklist check
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
        jti = jwt_payload["jti"]
        token = TokenBlocklist.query.filter_by(jti=jti).scalar()
        return token is not None

    # Register blueprints exactly as requested in Section 4.2
    from app.routes.health import health_bp
    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp, activities_bp # ADDED: activities_bp

    # Register error handlers and setup Python logging
    setup_logging(app) # ADDED: Initializes dev/prod logging and request middleware
    register_error_handlers(app)

    app.register_blueprint(health_bp, url_prefix='/api/health')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(activities_bp, url_prefix='/api/activities') # ADDED: Registers the Phase 3 endpoint

    return app