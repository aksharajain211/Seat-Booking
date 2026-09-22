from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for
)

from flask_login import login_required

from app.models.show import Show


show_bp = Blueprint(
    "show",
    __name__,
    url_prefix="/shows"
)


# -----------------------------------------
# Show all available shows
# -----------------------------------------

@show_bp.route("/")
def shows():

    shows = Show.query.order_by(
        Show.start_time
    ).all()

    return render_template(
        "shows/shows.html",
        shows=shows
    )


# -----------------------------------------
# Open a particular show
# -----------------------------------------

@show_bp.route("/<int:show_id>")
@login_required
def show_details(show_id):

    show = Show.query.get_or_404(
        show_id
    )

    # Directly move the user to
    # the seat-selection page.

    return redirect(
        url_for(
            "booking.seats",
            show_id=show.id
        )
    )