from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import User
from database import db

# Define the Blueprint
main_routes = Blueprint('main_routes', __name__)

# Route for selecting role (Student, Alumni, or Professor)
@main_routes.route('/select_role', methods=['GET', 'POST'])
def select_role():
    if request.method == 'POST':
        role = request.form.get('role')
        if role == 'alumni':
            # Redirect directly to alumni login page
            return redirect(url_for('main_routes.login', role='alumni'))
        elif role == 'student':
            # Redirect directly to student login page
            return redirect(url_for('main_routes.login', role='student'))
        elif role == 'professor':
            # Redirect directly to professor login page
            return redirect(url_for('main_routes.login', role='professor'))
        else:
            flash('Please select a valid role.', 'error')  # If no role is selected, show error
    return render_template('select_role.html')  # Render select_role page

# Redirect the default route to the role selection page
@main_routes.route('/')
def home():
    return redirect(url_for('main_routes.select_role'))  # Redirect to the role selection page

# Route for account creation (alumni, student, or professor)
@main_routes.route('/create_account', methods=['GET', 'POST'])
def create_account():
    role = request.args.get('role')

    # Check if role is valid
    if not role or role not in ['alumni', 'student', 'professor']:
        return render_template('select_role.html', error="Please select a valid role to create an account.")

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if role == 'alumni':
            grad_year = request.form.get('grad_year')
            # Create new alumni user
            new_user = User(name=name, email=email, password=password, role='alumni', grad_year=grad_year)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('main_routes.welcome', user_name=name))

        elif role == 'student':
            course = request.form.get('course')
            # Create new student user
            new_user = User(name=name, email=email, password=password, role='student', course=course)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('main_routes.welcome', user_name=name))

        elif role == 'professor':
            department = request.form.get('department')
            # Create new professor user
            new_user = User(name=name, email=email, password=password, role='professor', department=department)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('main_routes.welcome', user_name=name))

    # Dynamically construct the template path for account creation
    template_path = f'{role}/create_account_{role}.html'
    return render_template(template_path, role=role)

# Route for logging in
@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get('role', 'alumni').lower()  # Default to alumni if no role specified
    if role not in ['alumni', 'student', 'professor']:
        flash('Invalid role specified.', 'error')
        return redirect(url_for('main_routes.select_role'))  # Redirect to role selection page

    # Dynamically construct the template path for login
    template_path = f'{role}/login.html'

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')  # Password for authentication
        user = User.query.filter_by(email=email).first()

        if user and user.password == password:  # Check if the password is correct
            session['email'] = email

            # Redirect to correct profile based on user role
            if user.role == 'alumni':
                return redirect(url_for('main_routes.profile_alumni'))  # Redirect to alumni profile
            elif user.role == 'student':
                return redirect(url_for('main_routes.profile_student'))  # Redirect to student profile
            elif user.role == 'professor':
                return redirect(url_for('main_routes.profile_professor'))  # Redirect to professor profile
        else:
            flash('No account found with this email or incorrect password.', 'error')
            return render_template(template_path)  # Render login template if login fails

    return render_template(template_path)  # Render the login page


# Route for alumni profile
@main_routes.route('/profile_alumni', methods=['GET'])
def profile_alumni():
    user_email = session.get('email')
    user = User.query.filter_by(email=user_email).first()

    if not user or user.role != 'alumni':
        flash('Unauthorized access. Please login.', 'error')
        return redirect(url_for('main_routes.login', role='alumni'))  # Redirect to alumni login if not logged in

    return render_template('profile_alumni.html', user=user)

# Route for student profile
@main_routes.route('/profile_student', methods=['GET'])
def profile_student():
    user_email = session.get('email')
    user = User.query.filter_by(email=user_email).first()

    if not user or user.role != 'student':
        flash('Unauthorized access. Please login.', 'error')
        return redirect(url_for('main_routes.login', role='student'))  # Redirect to student login if not logged in

    return render_template('profile_student.html', user=user)

# Route for professor profile
@main_routes.route('/profile_professor', methods=['GET'])
def profile_professor():
    user_email = session.get('email')
    user = User.query.filter_by(email=user_email).first()

    if not user or user.role != 'professor':
        flash('Unauthorized access. Please login.', 'error')
        return redirect(url_for('main_routes.login', role='professor'))  # Redirect to professor login if not logged in

    return render_template('profile_professor.html', user=user)

# Route to welcome the user after successful account creation
@main_routes.route('/welcome/<user_name>')
def welcome(user_name):
    return render_template('welcome.html', user_name=user_name)

# Route for logging out
@main_routes.route('/logout')
def logout():
    session.pop('email', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main_routes.login', role='alumni'))  # Redirect to alumni login after logout