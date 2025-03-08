from flask import Flask
from backend.database import db, init_db
from backend.routes import main_routes

def create_app():
    """
    Application factory for the Flask app.
    """
    app = Flask(__name__)

    # Load configuration from backend.config
    app.config.from_object('backend.config')

    # Initialize the database with the app
    init_db(app)

    # Register the main routes blueprint
    app.register_blueprint(main_routes, url_prefix='/')

    return app
