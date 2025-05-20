from backend.database import db
from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship, backref

class User(db.Model):
    """
    User model for storing user data like name, email, password, and date of birth.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)  # Plain text password
    dob = db.Column(db.Date, nullable=True)
    role = db.Column(Enum('professor', 'alumni', 'student', name='user_roles'), nullable=False)

    student_profile = relationship('Student', backref=backref('user', uselist=False, cascade="all, delete"))
    alumni_profile = relationship('Alumni', backref=backref('user', uselist=False, cascade="all, delete"))
    professor_profile = relationship('Professor', backref=backref('user', uselist=False, cascade="all, delete"))

    def __init__(self, name, email, password, role, dob=None):
        self.name = name
        self.email = email
        self.set_password(password)
        self.dob = dob
        self.role = role

    def set_password(self, password):
        """Set the password (plain text)."""
        self.password = password

    def check_password(self, password):
        """Check if the provided password matches the stored password."""
        return self.password == password

    def __repr__(self):
        return f"<User id={self.id} name={self.name} email={self.email} role={self.role}>"

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    course = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(20), nullable=False)
    enrolled_year = db.Column(db.Integer, nullable=False)  # <-- Not nullable!
    degree = db.Column(db.String(100), nullable=True)
    specialization = db.Column(db.String(100), nullable=True)
    

    def __init__(self, id, course, year, enrolled_year=None, degree=None, specialization=None):
        self.id = id
        self.course = course
        self.year = year
        self.enrolled_year = enrolled_year
        self.degree = degree
        self.specialization = specialization

    def __repr__(self):
        return f"<Student id={self.id} course={self.course} year={self.year}>"

    def __str__(self):
        return f"Student: {self.course} ({self.year})"

class Alumni(db.Model):
    __tablename__ = 'alumni'
    id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    graduation_year = db.Column(db.String(10), nullable=False)  # <-- Change to String
    company = db.Column(db.String(100), nullable=True)
    degree = db.Column(db.String(100), nullable=True)
    specialization = db.Column(db.String(100), nullable=True)
    job_title = db.Column(db.String(100), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    work_exp = db.Column(db.Integer, nullable=True)

    def __init__(self, id, graduation_year, company=None, degree=None, specialization=None, job_title=None, industry=None, work_exp=None):
        self.id = id
        self.graduation_year = graduation_year
        self.company = company
        self.degree = degree
        self.specialization = specialization
        self.job_title = job_title
        self.industry = industry
        self.work_exp = work_exp

    def __repr__(self):
        return f"<Alumni id={self.id} graduation_year={self.graduation_year} company={self.company}>"

    def __str__(self):
        return f"Alumni: Graduated in {self.graduation_year}, Company: {self.company}"

class Professor(db.Model):
    __tablename__ = 'professors'
    id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    department = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(15), nullable=False)  # <-- Add this, not nullable!
    office = db.Column(db.String(50), nullable=True)
    experience = db.Column(db.Integer, nullable=True)

    def __init__(self, id, department, phone_number, office=None, designation=None, experience=None):
        self.id = id
        self.department = department
        self.phone_number = phone_number
        self.office = office
        self.designation = designation
        self.experience = experience

    def __repr__(self):
        return f"<Professor id={self.id} department={self.department} office={self.office}>"

    def __str__(self):
        return f"Professor: {self.department}, Office: {self.office}"