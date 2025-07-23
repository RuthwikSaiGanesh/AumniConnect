from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from backend.models import User, Student, Alumni, Professor
from backend.database import db
from datetime import datetime
import csv
import io

from flask import make_response

main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/')
def home():
    return render_template('home.html')


@main_routes.route('/select_role', methods=['GET', 'POST'])
def select_role():
    if request.method == 'POST':
        role = request.form.get('role')
        if role in ['alumni', 'student', 'professor']:
            return redirect(url_for('main_routes.login', role=role))
        flash('Please select a valid role.', 'error')
    else:
        role = request.args.get('role')
        if role == 'admin':
            return redirect(url_for('main_routes.admin_login'))
    return render_template('select_role.html')

@main_routes.route('/search')
def search():
    return render_template('search.html')

@main_routes.route('/api/search_users')
def api_search_users():
    q = request.args.get('q', '').strip()
    if not q:
        return []

    users = User.query.filter(User.name.ilike(f'%{q}%')).limit(10).all()

    results = []
    for user in users:
        profile_pic = url_for('static', filename='profile_placeholder.png')
        results.append({
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'profile_pic': profile_pic
        })
    return results

@main_routes.route('/update_professor_profile', methods=['POST'])
def update_professor_profile():
    email = session.get('email')
    user = User.query.filter_by(email=email, role='professor').first()
    if not user:
        flash('Unauthorized access. Please login.', 'error')
        return redirect(url_for('main_routes.login', role='professor'))

    about = request.form.get('about')
    education = request.form.get('education')
    experience = request.form.get('experience')
    skills = request.form.get('skills')

    # Here you would update the professor's profile fields in the database
    # For demonstration, assume these fields exist on the Professor model or related tables
    # You may need to adjust based on your actual data model

    # Example: store these fields as JSON or text in a profile table or columns
    # For now, just flash a message and redirect

    flash('Profile updated successfully.', 'success')
    return redirect(url_for('main_routes.profile_p'))

@main_routes.route('/update_alumni_profile', methods=['POST'])
def update_alumni_profile():
    email = session.get('email')
    user = User.query.filter_by(email=email, role='alumni').first()
    if not user:
        flash('Unauthorized access. Please login.', 'error')
        return redirect(url_for('main_routes.login', role='alumni'))

    # Similar update logic for alumni profile fields

    flash('Profile updated successfully.', 'success')
    return redirect(url_for('main_routes.profile_alumni'))

@main_routes.route('/update_student_profile', methods=['POST'])
def update_student_profile():
    email = session.get('email')
    user = User.query.filter_by(email=email, role='student').first()
    if not user:
        flash('Unauthorized access. Please login.', 'error')
        return redirect(url_for('main_routes.login', role='student'))

    # Similar update logic for student profile fields

    flash('Profile updated successfully.', 'success')
    return redirect(url_for('main_routes.profile'))

@main_routes.route('/create_account', methods=['GET', 'POST'])
def create_account():
    role = request.args.get('role') or request.form.get('role')
    if not role or role not in ['alumni', 'student', 'professor', 'admin']:
        return render_template('select_role.html', error="Please select a valid role to create an account.")

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email').lower()
        password = request.form.get('password')
        dob_str = request.form.get('dob')
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date() if dob_str else None

        try:
            new_user = User(name=name, email=email, password=password, role=role, dob=dob)
            db.session.add(new_user)
            db.session.flush()

            if role == 'alumni':
                alumni = Alumni(
                    id=new_user.id,
                    graduation_year=request.form.get('graduation_year'),
                    company=request.form.get('company'),
                    degree=request.form.get('degree'),
                    specialization=request.form.get('specialization'),
                    job_title=request.form.get('job_title'),
                    industry=request.form.get('industry'),
                    work_exp=request.form.get('work_exp')
                )
                db.session.add(alumni)

            elif role == 'student':
                student = Student(
                    id=new_user.id,
                    course=request.form.get('course'),
                    year=request.form.get('year'),
                    enrolled_year=request.form.get('enrolled_year'),
                    degree=request.form.get('degree'),
                    specialization=request.form.get('specialization')
                )
                db.session.add(student)

            elif role == 'professor':
                professor = Professor(
                    id=new_user.id,
                    department=request.form.get('department'),
                    designation=request.form.get('designation'),
                    phone_number=request.form.get('phone_number'),
                    office=request.form.get('office')
                )
                db.session.add(professor)

            elif role == 'admin':
    # Optionally store extra admin-related fields if needed
    # For now, we just rely on the main User table for admins
    # Ensure you have logic to identify admin in dashboard or login
                session['admin'] = True
                return redirect(url_for("main_routes.admin_dashboard"))


            db.session.commit()
            session['email'] = email
            if role == "student":
                return redirect(url_for("main_routes.profile"))
            elif role == "professor":
                return redirect(url_for("main_routes.profile_p"))
            elif role == "alumni":
                return redirect(url_for("main_routes.profile_alumni"))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", 'error')
            return render_template(f'{role}/create_account_{role}.html', error="An error occurred. Please try again.")

    return render_template(f'{role}/create_account_{role}.html', role=role)

@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get('role', 'alumni').lower()
    if role not in ['alumni', 'student', 'professor','admin']:
        flash('Invalid role specified.', 'error')
        return redirect(url_for('main_routes.select_role'))

    template_path = f'{role}/login.html'

    if request.method == 'POST':
        email = request.form.get('email', '').lower()
        password = request.form.get('password')
        user = User.query.filter_by(email=email, role=role).first()

        if user and user.check_password(password):
            session['email'] = email
            if role == "student":
                return redirect(url_for("main_routes.profile"))
            elif role == "professor":
                return redirect(url_for("main_routes.profile_p"))
            elif role == "alumni":
                return redirect(url_for("main_routes.profile_alumni"))
            elif role == "admin":
                return redirect(url_for("main_routes.DBMSAdmin"))
        else:
            flash('Invalid email or password.', 'error')
            return render_template(template_path, error="Invalid email or password.")

    return render_template(template_path)

@main_routes.route('/profile_alumni')
def profile_alumni():
    email = session.get('email')
    user = User.query.filter_by(email=email).first()
    if not user or user.role != 'alumni':
        flash('Unauthorized access. Please login.', 'error')
        return redirect(url_for('main_routes.login', role='alumni'))

    alumni = Alumni.query.filter_by(id=user.id).first()
    return render_template('alumni/profile_alumni.html', user=user, alumni=alumni)

@main_routes.route('/profile')
def profile():
    email = session.get('email')
    user = User.query.filter_by(email=email).first()
    if not user or user.role != 'student':
        flash('Unauthorized access. Please login.', 'error')
        return redirect(url_for('main_routes.login', role='student'))

    student = Student.query.filter_by(id=user.id).first()
    return render_template('student/profile.html', user=user, student=student)

@main_routes.route('/profile_p')
def profile_p():
    email = session.get('email')
    user = User.query.filter_by(email=email).first()
    if not user or user.role != 'professor':
        flash('Unauthorized access. Please login.', 'error')
        return redirect(url_for('main_routes.login', role='professor'))

    professor = Professor.query.filter_by(id=user.id).first()
    return render_template('professor/profile_p.html', user=user, professor=professor)

@main_routes.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main_routes.home'))

@main_routes.route('/settings')
def settings():
    return render_template('select_roleSETTINGS.html')

@main_routes.route('/admin')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('main_routes.admin_login'))

    users = User.query.all()
    columns = User.__table__.columns.keys()
    user_dicts = [u.__dict__ for u in users]
    for u in user_dicts:
        u.pop('_sa_instance_state', None)
    return render_template('admin_dashboard.html', users=user_dicts, columns=columns)

@main_routes.route('/download_users')
def download_users():
    if not session.get('admin'):
        flash('Admin access required.', 'error')
        return redirect(url_for('main_routes.admin_login'))

    users = User.query.all()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Name', 'Email', 'Role', 'DOB'])
    for user in users:
        cw.writerow([user.id, user.name, user.email, user.role, user.dob])
    
    response = make_response(si.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=users.csv"
    response.headers["Content-type"] = "text/csv"
    return response

@main_routes.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Replace with your admin credentials check
        if username == 'RuthwikSaiGanesh' and password == 'Rusaga@252817':
            session['admin'] = True
            session['email'] = username  # Set email in session to pass before_request check
            session['role'] = 'admin'    # Optionally set role
            return redirect(url_for('main_routes.DBMSAdmin'))
        else:
            error = "Invalid admin credentials."
    return render_template('admin_login.html', error=error)

@main_routes.route('/DBMSAdmin', methods=['GET', 'POST'])
def DBMSAdmin():
    # Only allow admin
    if not session.get('admin'):
        flash('Admin access required.', 'error')
        return redirect(url_for('main_routes.admin_login'))

    # Fetch all users for the table
    users = User.query.all()
    columns = ['id', 'name', 'email', 'password', 'role', 'dob']  # Added 'password' column

    # Convert users to list of dicts for Jinja2
    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'password': user.password,
            'role': user.role,
            'dob': user.dob.strftime('%Y-%m-%d') if user.dob else ''
        })

    return render_template('DBMSAdmin.html', users=users_data, columns=columns)

@main_routes.route('/dbmsadmin', methods=['GET', 'POST'])
def dbmsadmin_lowercase_redirect():
    return redirect(url_for('main_routes.DBMSAdmin'))

@main_routes.route('/add_user', methods=['POST'])
def add_user():
    if not session.get('admin'):
        flash('Admin access required.', 'error')
        return redirect(url_for('main_routes.admin_login'))
    name = request.form.get('name')
    email = request.form.get('email')
    role = request.form.get('role')
    dob = request.form.get('dob')
    user = User(name=name, email=email, role=role, dob=dob, password='default')
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('main_routes.DBMSAdmin'))

@main_routes.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if not session.get('admin'):
        flash('Admin access required.', 'error')
        return redirect(url_for('main_routes.admin_login'))

    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('main_routes.DBMSAdmin'))

    if request.method == 'POST':
        # Update user attributes from form data
        user.name = request.form.get('name')
        user.email = request.form.get('email').lower()
        user.password = request.form.get('password')  # Update password as well
        user.role = request.form.get('role')
        dob_str = request.form.get('dob')
        user.dob = datetime.strptime(dob_str, "%Y-%m-%d").date() if dob_str else None

        try:
            db.session.commit()
            flash('User updated successfully.', 'success')
            return redirect(url_for('main_routes.DBMSAdmin'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {e}', 'error')
            return render_template('edit_user.html', user=user)

    # GET request - render edit form
    return render_template('edit_user.html', user=user)

@main_routes.route('/delete_user', methods=['POST'])
def delete_user():
    if not session.get('admin'):
        flash('Admin access required.', 'error')
        return redirect(url_for('main_routes.admin_login'))
    user_id = request.args.get('user_id') or request.form.get('user_id')
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted.', 'success')
    else:
        flash('User not found.', 'error')
    return redirect(url_for('main_routes.DBMSAdmin'))

@main_routes.route('/add_student', methods=['POST'])
def add_student():
    if not session.get('admin'):
        flash('Admin access required.', 'error')
        return redirect(url_for('main_routes.admin_login'))
    try:
        name = request.form.get('name')
        email = request.form.get('email').lower()
        password = request.form.get('password')
        dob_str = request.form.get('dob')
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date() if dob_str else None
        course = request.form.get('course')
        year = request.form.get('year')
        enrolled_year = request.form.get('enrolled_year')
        degree = request.form.get('degree')
        specialization = request.form.get('specialization')

        new_user = User(name=name, email=email, password=password, role='student', dob=dob)
        db.session.add(new_user)
        db.session.flush()

        student = Student(
            id=new_user.id,
            course=course,
            year=year,
            enrolled_year=enrolled_year,
            degree=degree,
            specialization=specialization
        )
        db.session.add(student)
        db.session.commit()
        flash('Student added successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding student: {e}', 'error')
    return redirect(url_for('main_routes.DBMSAdmin'))

@main_routes.route('/add_professor', methods=['POST'])
def add_professor():
    if not session.get('admin'):
        flash('Admin access required.', 'error')
        return redirect(url_for('main_routes.admin_login'))
    try:
        name = request.form.get('name')
        email = request.form.get('email').lower()
        password = request.form.get('password')
        dob_str = request.form.get('dob')
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date() if dob_str else None
        department = request.form.get('department')
        designation = request.form.get('designation')
        phone_number = request.form.get('phone_number')
        office = request.form.get('office')
        experience = request.form.get('experience')

        new_user = User(name=name, email=email, password=password, role='professor', dob=dob)
        db.session.add(new_user)
        db.session.flush()

        professor = Professor(
            id=new_user.id,
            department=department,
            designation=designation,
            phone_number=phone_number,
            office=office,
            experience=experience
        )
        db.session.add(professor)
        db.session.commit()
        flash('Professor added successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding professor: {e}', 'error')
    return redirect(url_for('main_routes.DBMSAdmin'))

@main_routes.route('/add_alumni', methods=['POST'])
def add_alumni():
    if not session.get('admin'):
        flash('Admin access required.', 'error')
        return redirect(url_for('main_routes.admin_login'))
    try:
        name = request.form.get('name')
        email = request.form.get('email').lower()
        password = request.form.get('password')
        dob_str = request.form.get('dob')
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date() if dob_str else None
        graduation_year = request.form.get('graduation_year')
        company = request.form.get('company')
        degree = request.form.get('degree')
        specialization = request.form.get('specialization')
        job_title = request.form.get('job_title')
        industry = request.form.get('industry')
        work_exp = request.form.get('work_exp')

        new_user = User(name=name, email=email, password=password, role='alumni', dob=dob)
        db.session.add(new_user)
        db.session.flush()

        alumni = Alumni(
            id=new_user.id,
            graduation_year=graduation_year,
            company=company,
            degree=degree,
            specialization=specialization,
            job_title=job_title,
            industry=industry,
            work_exp=work_exp
        )
        db.session.add(alumni)
        db.session.commit()
        flash('Alumni added successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding alumni: {e}', 'error')
    return redirect(url_for('main_routes.DBMSAdmin'))
