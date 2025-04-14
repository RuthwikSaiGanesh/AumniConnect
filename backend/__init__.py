from flask import Flask
from flask_migrate import Migrate
from backend.database import db, init_db
from backend.routes import main_routes

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config.from_object('backend.config.DevelopmentConfig')

    # Initialize database and migrations
    init_db(app)
    migrate = Migrate(app, db)

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    # Register routes
    from backend.routes import main_routes
    app.register_blueprint(main_routes)

    return app