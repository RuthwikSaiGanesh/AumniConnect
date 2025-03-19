from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Date, Enum

class User(db.Model):
    """
    User model for storing user data like name, email, password, and date of birth.
    """
    id = db.Column(db.Integer, primary_key=True)  # Primary key for User
    name = db.Column(db.String(100), nullable=False)  # Name of the user
    email = db.Column(db.String(120), unique=True, nullable=False)  # User's unique email
    password = db.Column(db.String(200), nullable=False)  # Password (hashed)
    dob = db.Column(db.Date, nullable=True)
    role = db.Column(Enum('professor', 'alumni', 'student', name='user_roles'), nullable=False)  # Date of birth (using Date type)

    # Defining the constructor explicitly to accept name, email, password, and dob
    def __init__(self, name, email, password, role, dob=None):
        self.name = name
        self.email = email
        self.password = password
        self.dob = dob
        self.role = role

    # Set the password by hashing it
    def set_password(self, password):
        """Set the password after hashing it."""
        self.password = generate_password_hash(password)

    # Check if the provided password matches the stored hash
    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.name}>"