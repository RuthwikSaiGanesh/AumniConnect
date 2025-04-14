from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

# SQLAlchemy instance
db = SQLAlchemy()

# Define the engine (replace 'sqlite:///app.db' with your database URL)
engine = create_engine('sqlite:///app.db')  # Example for SQLite

def init_db(app):
    """
    Initialize the database with the Flask app.
    Bind the app with the database instance and create tables if they don't exist already.
    """
    db.init_app(app)  # Bind the database instance to the Flask app

    # Create tables within the app context
    with app.app_context():
        db.create_all()  # Create tables based on the models