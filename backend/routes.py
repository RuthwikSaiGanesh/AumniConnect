from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from backend.models import User, Student, Alumni, Professor
from backend.database import db
from datetime import datetime

# Define the Blueprint
main_routes = Blueprint('main_routes', __name__)

# Route for selecting role (Student, Alumni, or Professor)
@main_routes.route('/select_role', methods=['GET', 'POST'])
def select_role():
    if request.method == 'POST':
        role = request.form.get('role')
        if role == 'alumni':
            return redirect(url_for('main_routes.login', role='alumni'))
        elif role == 'student':
            return redirect(url_for('main_routes.login', role='student'))
        elif role == 'professor':
            return redirect(url_for('main_routes.login', role='professor'))
        else:
            flash('Please select a valid role.', 'error')
    return render_template('select_role.html')

# Redirect the default route to the role selection page
@main_routes.route('/')
def home():
    return redirect(url_for('main_routes.select_role'))

# Route for account creation (alumni, student, or professor)
@main_routes.route('/create_account', methods=['GET', 'POST'])
def create_account():
    role = request.args.get('role')
    if not role or role not in ['alumni', 'student', 'professor']:
        return render_template('select_role.html', error="Please select a valid role to create an account.")

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        dob_str = request.form.get('dob')
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()

        # Create the User object
        new_user = User(name=name, email=email, password=password, role=role, dob=dob)
        new_user.set_password(password)  # Hash the password
        db.session.add(new_user)
        db.session.flush()  # Get the user ID before committing

        # Create role-specific objects
        if role == 'alumni':
            grad_year = request.form.get('grad_year')
            company = request.form.get('company')
            alumni = Alumni(id=new_user.id, graduation_year=grad_year, company=company)
            db.session.add(alumni)

        elif role == 'student':
            course = request.form.get('course')
            year = request.form.get('year')
            student = Student(id=new_user.id, course=course, year=year)
            db.session.add(student)

        elif role == 'professor':
            department = request.form.get('department')
            office = request.form.get('office')
            professor = Professor(id=new_user.id, department=department, office=office)
            db.session.add(professor)

        db.session.commit()

        # Log the user in
        session['email'] = email

        # Redirect to a welcome page or profile page based on the role
        if role == 'alumni':
            return redirect(url_for('main_routes.profile_alumni'))
        elif role == 'student':
            return redirect(url_for('main_routes.profile_student'))
        elif role == 'professor':
            return redirect(url_for('main_routes.profile_professor'))

    # Dynamically construct the template path for account creation
    template_path = f'{role}/create_account_{role}.html'
    return render_template(template_path, role=role)

# Route for logging in
@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get('role', 'alumni').lower()  # Default to alumni if no role is provided
    if role not in ['alumni', 'student', 'professor']:
        flash('Invalid role specified.', 'error')
        return redirect(url_for('main_routes.select_role'))

    template_path = f'{role}/login.html'

    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):  # Use the check_password method
            session['email'] = email
            if role == 'alumni':
                return render_template('alumni/welcome.html', user=user)
            elif role == 'student':
                return render_template('student/welcome.html', user=user)
            elif role == 'professor':
                return render_template('professor/welcome.html', user=user)
        else:
            flash('Invalid email or password.', 'error')
            return render_template(template_path, error="Invalid email or password.")

    return render_template(template_path)

# Route for alumni profile
@main_routes.route('/profile_alumni', methods=['GET'])
def profile_alumni():
    user_email = session.get('email')
    user = User.query.filter_by(email=user_email).first()

    if not user or user.role != 'alumni':
        flash('Unauthorized access. Please login.', 'error')
        return redirect(url_for('main_routes.login', role='alumni'))

    alumni = Alumni.query.filter_by(id=user.id).first()
    return render_template('alumni/profile_alumni.html', user=user, alumni=alumni)

# Route for student profile
@main_routes.route('/profile_student', methods=['GET'])
def profile_student():
    user_email = session.get('email')
    user = User.query.filter_by(email=user_email).first()

    if not user or user.role != 'student':
        flash('Unauthorized access. Please login.', 'error')
        return redirect(url_for('main_routes.login', role='student'))

    student = Student.query.filter_by(id=user.id).first()
    return render_template('student/profile_student.html', user=user, student=student)

# Route for professor profile
@main_routes.route('/profile_professor', methods=['GET'])
def profile_professor():
    user_email = session.get('email')
    user = User.query.filter_by(email=user_email).first()

    if not user or user.role != 'professor':
        flash('Unauthorized access. Please login.', 'error')
        return redirect(url_for('main_routes.login', role='professor'))

    professor = Professor.query.filter_by(id=user.id).first()
    return render_template('professor/profile_professor.html', user=user, professor=professor)

# Route to welcome the user after successful account creation
@main_routes.route('/welcome/<user_name>')
def welcome(user_name):
    return render_template('welcome.html', user_name=user_name)

# Route for logging out
@main_routes.route('/logout')
def logout():
    session.pop('email', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main_routes.home'))