from flask import Flask, render_template
from backend import db, init_db
from backend.routes import main_routes

def create_app():
    """
    Application factory for the Flask app.
    """
    app = Flask(__name__)

    # Load configuration from backend.config
    app.config.from_object('backend.config.Config')

    # Initialize the database with the app
    init_db(app)

    # Register the Blueprint
    app.register_blueprint(main_routes, url_prefix='/')

    # Set up session management
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Error handling routes
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('500.html'), 500

    return app


if __name__ == "__main__":
    app = create_app()
    host = "127.0.0.1"
    port = 5000
    print(f"\nServer running at: \033[94mhttp://{host}:{port}/\033[0m")  # Clickable link in some terminals
    print("Press Ctrl+C to stop.\n")
    app.run(debug=True, host=host, port=port)
