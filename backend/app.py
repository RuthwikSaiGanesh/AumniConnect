from flask import Flask, render_template, session, request, redirect, url_for
from config import Config
from models import User

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    from flask_sqlalchemy import SQLAlchemy
    from database import db, init_db
    app.config.from_object(Config)
    init_db(app)
    # Import main_routes inside create_app() to avoid circular import
    from routes import main_routes

    app.register_blueprint(main_routes)

    @app.route('/')
    def index():
        if 'email' in session:
            return redirect(url_for('main_routes.home'))
        return redirect(url_for('main_routes.select_role'))

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('500.html'), 500

    @app.before_request
    def check_logged_in():
        public_endpoints = ['main_routes.select_role', 'main_routes.login', 'main_routes.create_account', 'static']
        if 'email' not in session and request.endpoint not in public_endpoints:
            return redirect(url_for('main_routes.select_role'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.config.from_object('config.DevelopmentConfig')
    app.run(port=5000, debug=True)
