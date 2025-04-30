from flask import Flask, render_template, session, request, redirect, url_for
from backend.config import Config
from backend.database import db, init_db
from backend.models import User  # Assuming User is defined in backend.models
from flask_migrate import Migrate
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash

def create_app():
    """
    Factory function to create and configure the Flask application.
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config.from_object('backend.config.DevelopmentConfig')

    # Initialize database and migrations
    init_db(app)
    migrate = Migrate(app, db)

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    # Register routes
    from backend.routes import main_routes
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
        """
        Middleware to check if the user is logged in before accessing protected routes.
        """
        public_endpoints = ['main_routes.select_role', 'main_routes.login', 'main_routes.create_account', 'static']
        if 'email' not in session and request.endpoint not in public_endpoints:
            return redirect(url_for('main_routes.select_role'))

    return app


# ==========================
# CLI-based DBMS Management
# ==========================

def add_user():
    """
    Add a new user to the database via CLI.
    """
    name = input("Enter user name: ").strip()
    email = input("Enter user email: ").strip()
    password = input("Enter user password: ").strip()
    role = input("Enter user role (student/professor/alumni/etc): ").strip()

    if not name or not email or not password or not role:
        print("❌ All fields are required.")
        return

    hashed_password = generate_password_hash(password)
    print(f"🔒 Hashed password: {hashed_password}")  # Debugging log

    try:
        # Create a session within the application context
        with create_app().app_context():
            print("✅ App context created.")  # Debugging log
            Session = sessionmaker(bind=db.engine)
            with Session() as session_db:
                print("✅ Database session created.")  # Debugging log

                # Create a new user instance
                user = User(name=name, email=email, password=hashed_password, role=role)
                print(f"📝 Adding user: {user}")  # Debugging log
                session_db.add(user)
                session_db.commit()
                print(f"✅ User '{name}' added successfully!")
    except SQLAlchemyError as e:
        print(f"❌ Error adding user: {e}")


def view_users():
    """
    View all users in the database via CLI.
    """
    try:
        # Create a session within the application context
        with create_app().app_context():
            Session = sessionmaker(bind=db.engine)
            with Session() as session_db:
                users = session_db.query(User).all()
                if not users:
                    print("❌ No users found.")
                else:
                    print("📄 Users in database:")
                    for user in users:
                        print(f"ID: {user.id}, Name: {user.name}, Email: {user.email}, Role: {user.role}")
    except SQLAlchemyError as e:
        print(f"❌ Error viewing users: {e}")


def search_user():
    """
    Search for a user by name via CLI.
    """
    keyword = input("🔍 Enter name to search: ").strip()
    try:
        # Create a session within the application context
        with create_app().app_context():
            Session = sessionmaker(bind=db.engine)
            with Session() as session_db:
                users = session_db.query(User).filter(User.name.ilike(f"%{keyword}%")).all()
                if not users:
                    print("❌ No matching users found.")
                else:
                    print("🔎 Search results:")
                    for user in users:
                        print(f"ID: {user.id}, Name: {user.name}, Email: {user.email}, Role: {user.role}")
    except SQLAlchemyError as e:
        print(f"❌ Error searching users: {e}")


def update_user():
    """
    Update a user's role in the database via CLI.
    """
    try:
        user_id = int(input("Enter user ID to update: "))
    except ValueError:
        print("❌ Invalid ID.")
        return

    new_role = input("Enter new role: ").strip()
    if not new_role:
        print("❌ Role cannot be empty.")
        return

    try:
        # Create a session within the application context
        with create_app().app_context():
            Session = sessionmaker(bind=db.engine)
            with Session() as session_db:
                user = session_db.query(User).filter_by(id=user_id).first()
                if user:
                    old_role = user.role
                    user.role = new_role
                    session_db.commit()
                    print(f"✏ Updated '{user.name}' from role '{old_role}' to '{new_role}'.")
                else:
                    print("❌ User not found.")
    except SQLAlchemyError as e:
        print(f"❌ Error updating user: {e}")


def delete_user():
    """
    Delete a user from the database via CLI.
    """
    try:
        user_id = int(input("Enter user ID to delete: "))
    except ValueError:
        print("❌ Invalid ID.")
        return

    try:
        # Create a session within the application context
        with create_app().app_context():
            Session = sessionmaker(bind=db.engine)
            with Session() as session_db:
                user = session_db.query(User).filter_by(id=user_id).first()
                if user:
                    confirm = input(f"⚠ Are you sure you want to delete '{user.name}'? (y/n): ").lower()
                    if confirm == 'y':
                        session_db.delete(user)
                        session_db.commit()
                        print(f"🗑 User '{user.name}' deleted.")
                    else:
                        print("❌ Deletion cancelled.")
                else:
                    print("❌ User not found.")
    except SQLAlchemyError as e:
        print(f"❌ Error deleting user: {e}")


# ========================
# Entrypoint Switch
# ========================
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'cli':
        while True:
            print("\n📋 Choose an option:")
            print("1. Add user")
            print("2. View users")
            print("3. Search user by name")
            print("4. Update user role")
            print("5. Delete user")
            print("6. Exit")

            choice = input("Enter choice: ")

            if choice == '1':
                add_user()
            elif choice == '2':
                view_users()
            elif choice == '3':
                search_user()
            elif choice == '4':
                update_user()
            elif choice == '5':
                delete_user()
            elif choice == '6':
                print("👋 Exiting CLI...")
                break
            else:
                print("❌ Invalid choice, try again.")
    else:
        app = create_app()
        app.run(port=5000, debug=True)