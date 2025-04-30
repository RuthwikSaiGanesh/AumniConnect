import os

class Config:
    """
    Base configuration class with default settings.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')  # Default secret key
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Base directory of the project
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking to save resources
    LOGIN_MANAGER_LOGIN_VIEW = 'main_routes.login'  # Default login view route


class DevelopmentConfig(Config):
    """
    Configuration for development environment.
    """
    DEBUG = True
    # Use MySQL for development
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:252817@localhost:3306/Project_manager'


class ProductionConfig(Config):
    """
    Configuration for production environment.
    """
    DEBUG = False
    # Use PostgreSQL or other DB in production
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://user:password@localhost/db_name'
    )


class TestingConfig(Config):
    """
    Configuration for testing environment.
    """
    TESTING = True
    # Use SQLite for testing
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(Config.BASE_DIR, 'test_db.db')}"


# Dictionary to map configuration names to classes
config_by_name = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'test': TestingConfig
}