import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # It is perfectly fine (and encouraged!) to have fallbacks here for local development.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-secret-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-fallback-jwt-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # Overriding keys for tests to ensure pytest never crashes due to a missing .env
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'this-is-a-super-secret-test-key-32-chars'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # In production, we don't want to inherit the dev fallbacks, so we attempt to grab the real ones again
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

# THE GUARD: This fulfills Observation 2.6
# It checks if we are in production, and if so, strictly enforces the presence of the security keys.
if os.environ.get('FLASK_ENV') in ['prod', 'production']:
    if not os.environ.get('SECRET_KEY') or not os.environ.get('JWT_SECRET_KEY'):
        raise ValueError("CRITICAL: SECRET_KEY and JWT_SECRET_KEY must be explicitly set in the production environment!")

config_by_name = {
    'dev': DevelopmentConfig,
    'development': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig,
    'production': ProductionConfig
}