from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

db = SQLAlchemy()

def init_db(app):
    """
    Initialize the SQLAlchemy database with the Flask app.
    """
    db.init_app(app)

# --- SQLAlchemy helper functions for raw SQL queries ---

def fetch_one(query, params=None):
    """
    Execute a SELECT query and fetch a single result as a dict.
    Usage: user = fetch_one("SELECT * FROM users WHERE email = :email", {"email": email})
    """
    try:
        result = db.session.execute(text(query), params or {})
        row = result.fetchone()
        if row:
            return dict(row)
        return None
    except SQLAlchemyError as e:
        print(f"❌ SQLAlchemy error: {e}")
        return None

def fetch_all(query, params=None):
    """
    Execute a SELECT query and fetch all results as a list of dicts.
    Usage: users = fetch_all("SELECT * FROM users WHERE role = :role", {"role": "alumni"})
    """
    try:
        result = db.session.execute(text(query), params or {})
        rows = result.fetchall()
        return [dict(row) for row in rows]
    except SQLAlchemyError as e:
        print(f"❌ SQLAlchemy error: {e}")
        return []

def execute_query_with_params(query, params=None):
    """
    Execute an INSERT/UPDATE/DELETE query with parameters.
    Usage: execute_query_with_params(
        "INSERT INTO users (name, email, password, role) VALUES (:name, :email, :password, :role)",
        {"name": name, "email": email, "password": password, "role": role}
    )
    """
    try:
        db.session.execute(text(query), params or {})
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        print(f"❌ SQLAlchemy error: {e}")
        db.session.rollback()
        return False

def get_last_insert_id():
    """
    Get the last inserted ID from the database.
    Note: This works for MySQL.
    """
    try:
        result = db.session.execute(text("SELECT LAST_INSERT_ID()"))
        last_id = result.scalar()
        return last_id
    except SQLAlchemyError as e:
        print(f"❌ SQLAlchemy error: {e}")
        return None