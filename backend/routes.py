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
    return redirect(url_for('main_routes.select_role'))

@main_routes.route('/select_role', methods=['GET', 'POST'])
def select_role():
    if request.method == 'POST':
        role = request.form.get('role')
        if role in ['alumni', 'student', 'professor']:
            return redirect(url_for('main_routes.login', role=role))
        if role == 'admin':
            # Added this to handle Admin button click in select_role.html
            return redirect(url_for('main_routes.admin_login'))
        flash('Please select a valid role.', 'error')
    return render_template('select_role.html')

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

        if user and user.password == password:
            session['email'] = email
            if role == "student":
                return redirect(url_for("main_routes.profile"))
            elif role == "professor":
                return redirect(url_for("main_routes.profile_p"))
            elif role == "alumni":
                return redirect(url_for("main_routes.profile_alumni"))
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

@main_routes.route('/admin_dashboard')
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

@main_routes.route('/admin', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Replace with your admin credentials check
        if username == 'RuthwikSaiGanesh' and password == 'Rusaga@252817':
            session['admin'] = True
            return redirect(url_for('main_routes.select_roleDBMS'))
        else:
            error = "Invalid admin credentials."
    return render_template('admin_login.html', error=error)

@main_routes.route('/dbms', methods=['GET', 'POST'])
def select_roleDBMS():
    # Only allow admin
    if not session.get('admin'):
        flash('Admin access required.', 'error')
        return redirect(url_for('main_routes.admin_login'))

    # Fetch all users for the table
    users = User.query.all()
    columns = ['id', 'name', 'email', 'role', 'dob']  # Add/remove columns as needed

    # Convert users to list of dicts for Jinja2
    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'dob': user.dob.strftime('%Y-%m-%d') if user.dob else ''
        })

    return render_template('select_roleDBMS.html', users=users_data, columns=columns)

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
    return redirect(url_for('main_routes.select_roleDBMS'))

@main_routes.route('/edit_user', methods=['POST'])
def edit_user():
    # For demo: just redirect, you can implement a full edit form if needed
    flash('Edit functionality not implemented in this demo.', 'info')
    return redirect(url_for('main_routes.Select_roleDBMS'))

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
    return redirect(url_for('main_routes.select_roleDBMS'))
