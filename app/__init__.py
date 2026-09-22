from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    # Import blueprints
    from app.routes.auth import auth_bp
    from app.routes.movie import movie_bp
    from app.routes.show import show_bp
    from app.routes.booking import booking_bp
    from app.routes.payment import payment_bp

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(movie_bp)
    app.register_blueprint(show_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(payment_bp)

    # Import models
    from app.models import import_models
    import_models()

    # Create database tables
    with app.app_context():
        db.create_all()

    # -----------------------------
    # HOME PAGE
    # -----------------------------
    @app.route("/")
    def home():
        return redirect(url_for("movie.movies"))

    return app