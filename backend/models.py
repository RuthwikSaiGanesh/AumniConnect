from backend.database import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Date, Enum

class User(db.Model):
    """
    User model for storing user data like name, email, password, and date of birth.
    """
    __tablename__ = 'users'  # Explicit table name for clarity
    id = db.Column(db.Integer, primary_key=True)  # Primary key for User
    name = db.Column(db.String(100), nullable=False)  # Name of the user
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)  # User's unique email with index
    password = db.Column(db.String(200), nullable=False)  # Password (hashed)
    dob = db.Column(db.Date, nullable=True)  # Date of birth
    role = db.Column(Enum('professor', 'alumni', 'student', name='user_roles'), nullable=False)  # Role field

    def __init__(self, name, email, password, role, dob=None):
        self.name = name
        self.email = email
        self.set_password(password)  # Hash the password during initialization
        self.dob = dob
        self.role = role

    def set_password(self, password):
        """Set the password after hashing it."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User id={self.id} name={self.name} email={self.email} role={self.role}>"


class Student(db.Model):
    """
    Student model for storing additional student-specific information.
    """
    __tablename__ = 'students'  # Explicit table name for clarity
    id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    course = db.Column(db.String(100), nullable=False)  # Course the student is enrolled in
    year = db.Column(db.String(20), nullable=False)  # Year of study
    user = db.relationship('User', backref=db.backref('student_profile', uselist=False, cascade="all, delete"))

    def __init__(self, id, course, year):
        self.id = id
        self.course = course
        self.year = year

    def __repr__(self):
        return f"<Student id={self.id} course={self.course} year={self.year}>"

    def __str__(self):
        return f"Student: {self.course} ({self.year})"


class Alumni(db.Model):
    """
    Alumni model for storing additional alumni-specific information.
    """
    __tablename__ = 'alumni'  # Explicit table name for clarity
    id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    graduation_year = db.Column(db.String(10), nullable=False)  # Year of graduation
    company = db.Column(db.String(100), nullable=True)  # Company the alumni is working at
    user = db.relationship('User', backref=db.backref('alumni_profile', uselist=False, cascade="all, delete"))

    def __init__(self, id, graduation_year, company=None):
        self.id = id
        self.graduation_year = graduation_year
        self.company = company

    def __repr__(self):
        return f"<Alumni id={self.id} graduation_year={self.graduation_year} company={self.company}>"

    def __str__(self):
        return f"Alumni: Graduated in {self.graduation_year}, Company: {self.company}"


class Professor(db.Model):
    """
    Professor model for storing additional professor-specific information.
    """
    __tablename__ = 'professors'  # Explicit table name for clarity
    id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    department = db.Column(db.String(100), nullable=False)  # Department the professor belongs to
    office = db.Column(db.String(50), nullable=True)  # Office location
    user = db.relationship('User', backref=db.backref('professor_profile', uselist=False, cascade="all, delete"))

    def __init__(self, id, department, office=None):
        self.id = id
        self.department = department
        self.office = office

    def __repr__(self):
        return f"<Professor id={self.id} department={self.department} office={self.office}>"

    def __str__(self):
        return f"Professor: {self.department}, Office: {self.office}"