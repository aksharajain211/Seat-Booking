from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required
)

from app import db, login_manager
from app.models.user import User


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        User,
        int(user_id)
    )


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash("Email already registered.")

            return redirect(
                url_for("auth.register")
            )

        user = User(
            name=name,
            email=email
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Registration successful.")

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "auth/register.html"
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()

        if user and user.check_password(password):

            login_user(user)

            return redirect(
                url_for("movie.movies")
            )

        flash("Invalid email or password.")

    return render_template(
        "auth/login.html"
    )


@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("movie.movies")
    )