import os

class Config:
    """
    Base configuration class with default settings.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')  # Default secret key
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Base directory of the project
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'aumni_connect.db')}"  # Default SQLite DB
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking to save resources
    LOGIN_MANAGER_LOGIN_VIEW = 'main_routes.login'  # Default login view route


class DevelopmentConfig(Config):
    """
    Configuration for development environment.
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(Config.BASE_DIR, 'alumnq_dev.db')}"  # SQLite for development


class ProductionConfig(Config):
    """
    Configuration for production environment.
    """
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://user:password@localhost/db_name'
    )  # Use PostgreSQL or other DB in production


class TestingConfig(Config):
    """
    Configuration for testing environment.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(Config.BASE_DIR, 'test_db.db')}"  # Separate DB for testing


# Dictionary to map configuration names to classes
config_by_name = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'test': TestingConfig
}