import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')  # Default secret key
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///alumnq.db')  # Default database URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOGIN_MANAGER_LOGIN_VIEW = 'main_routes.login'  # Corrected to match your route


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///alumnq.db'  # Use SQLite for dev


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost/db_name')  # Postgres for production


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_db.db'  # Use a separate SQLite DB for testing


config_by_name = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'test': TestingConfig
}
