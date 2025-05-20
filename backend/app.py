from flask import Flask, render_template, session, request, redirect, url_for, flash
from backend.config import Config
from backend.database import db, init_db, fetch_one, execute_query_with_params, get_last_insert_id
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config.from_object('backend.config.DevelopmentConfig')

    # Initialize database and migrations
    init_db(app)
    migrate = Migrate(app, db)

    with app.app_context():
        db.create_all()

    from backend.routes import main_routes
    app.register_blueprint(main_routes)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        role = request.args.get('role', '').lower()
        if role not in ['student', 'alumni', 'professor']:
            role = ''

        if request.method == 'POST':
            email = request.form.get('email', '').lower()
            password_input = request.form.get('password')

            try:
                user_query = "SELECT * FROM users WHERE email = :email AND role = :role"
                user = fetch_one(user_query, {"email": email, "role": role})

                if user and user['password'] == password_input:
                    session['email'] = user['email']
                    session['name'] = user['name']
                    session['role'] = user['role']
                    print(f"✅ Login successful for user: {user['name']}")

                    return redirect(url_for(f"{role}_welcome")) if role else redirect(url_for('index'))

                error = "Invalid email or password."
                print("❌ Invalid login.")
                return render_template(f'{role}/login.html' if role else 'login.html', error=error, role=role)
            except Exception as e:
                print(f"❌ Error during login: {e}")
                error = "An error occurred. Please try again."
                return render_template(f'{role}/login.html' if role else 'login.html', error=error, role=role)

        return render_template(f'{role}/login.html' if role else 'login.html', role=role)

    @app.route('/student/welcome')
    def student_welcome():
        if session.get('role') == 'student':
            return render_template('student/welcome.html', name=session.get('name'))
        return redirect(url_for('login'))

    @app.route('/alumni/welcome')
    def alumni_welcome():
        if session.get('role') == 'alumni':
            return render_template('alumni/welcome.html', name=session.get('name'))
        return redirect(url_for('login'))

    @app.route('/professor/welcome')
    def professor_welcome():
        if session.get('role') == 'professor':
            return render_template('professor/welcome.html', name=session.get('name'))
        return redirect(url_for('login'))

    @app.route('/')
    def index():
        if 'email' in session:
            role = session.get('role')
            return redirect(url_for(f"{role}_welcome")) if role else redirect(url_for('main_routes.select_role'))
        return redirect(url_for('main_routes.select_role'))

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('500.html'), 500

    @app.before_request
    def check_logged_in():
        public_endpoints = [
            'main_routes.select_role', 'main_routes.login', 'main_routes.create_account',
            'login', 'create_account', 'static'
        ]
        if 'email' not in session and request.endpoint not in public_endpoints:
            return redirect(url_for('main_routes.select_role'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)
