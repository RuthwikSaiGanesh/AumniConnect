from flask_sqlalchemy import SQLAlchemy

# Create an SQLAlchemy object to manage the database
db = SQLAlchemy()

def init_db(app):
    """
    Initialize the database with the Flask app.
    Bind the app with the database instance and create tables if they don't exist already.
    """
    db.init_app(app)  # Bind the database instance to the Flask app

    # Create tables only if they don't exist already (app context)
    with app.app_context():
        db.create_all()  # Create tables based on the models (ideal for dev, but use migrations in prod)
