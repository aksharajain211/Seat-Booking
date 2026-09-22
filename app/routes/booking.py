from datetime import datetime, timedelta

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    url_for,
    flash,
    redirect
)

from flask_login import login_required, current_user

from app import db

from app.models.show import Show
from app.models.seat import ShowSeat
from app.models.booking import Booking, BookingSeat


booking_bp = Blueprint(
    "booking",
    __name__,
    url_prefix="/booking"
)


# =========================================================
# SEAT SELECTION PAGE
# =========================================================

@booking_bp.route("/seats/<int:show_id>")
@login_required
def seats(show_id):

    show = Show.query.get_or_404(show_id)

    now = datetime.utcnow()

    # Get all seats for this show
    show_seats = (
        ShowSeat.query
        .filter_by(show_id=show.id)
        .order_by(
            ShowSeat.seat_id
        )
        .all()
    )

    # =====================================================
    # RELEASE EXPIRED HOLDS
    # =====================================================

    changed = False

    for show_seat in show_seats:

        if (
            show_seat.status == "HELD"
            and show_seat.hold_until
            and show_seat.hold_until <= now
        ):

            show_seat.status = "AVAILABLE"

            show_seat.held_by = None

            show_seat.hold_until = None

            changed = True


    if changed:

        db.session.commit()


    return render_template(
        "booking/seats.html",

        show=show,

        show_seats=show_seats
    )


# =========================================================
# HOLD SELECTED SEATS
# =========================================================

@booking_bp.route(
    "/hold-seats",
    methods=["POST"]
)
@login_required
def hold_seats():

    data = request.get_json(
        silent=True
    )


    # =====================================================
    # VALIDATE REQUEST
    # =====================================================

    if not data:

        return jsonify({

            "success": False,

            "message":
                "Invalid request."

        }), 400


    show_id = data.get(
        "show_id"
    )


    seat_ids = data.get(
        "seat_ids",
        []
    )


    if not show_id:

        return jsonify({

            "success": False,

            "message":
                "Show ID is missing."

        }), 400


    if not seat_ids:

        return jsonify({

            "success": False,

            "message":
                "Please select at least one seat."

        }), 400


    # Make sure IDs are integers
    try:

        seat_ids = [
            int(seat_id)
            for seat_id in seat_ids
        ]

    except (
        ValueError,
        TypeError
    ):

        return jsonify({

            "success": False,

            "message":
                "Invalid seat IDs."

        }), 400


    # Remove duplicate IDs

    seat_ids = list(
        dict.fromkeys(
            seat_ids
        )
    )


    try:

        # =================================================
        # GET SHOW
        # =================================================

        show = Show.query.get(
            show_id
        )


        if not show:

            return jsonify({

                "success": False,

                "message":
                    "Show not found."

            }), 404


        now = datetime.utcnow()


        # =================================================
        # GET SELECTED SHOW SEATS
        # =================================================

        seats = (
            ShowSeat.query
            .filter(
                ShowSeat.show_id == show.id,
                ShowSeat.id.in_(seat_ids)
            )
            .with_for_update()
            .all()
        )


        # =================================================
        # VALIDATE ALL SEATS EXIST
        # =================================================

        if len(seats) != len(seat_ids):

            db.session.rollback()

            return jsonify({

                "success": False,

                "message":
                    "One or more selected seats are invalid."

            }), 400


        # =================================================
        # RELEASE EXPIRED HOLDS
        # =================================================

        for seat in seats:

            if (
                seat.status == "HELD"
                and seat.hold_until
                and seat.hold_until <= now
            ):

                seat.status = "AVAILABLE"

                seat.held_by = None

                seat.hold_until = None


        db.session.flush()


        # =================================================
        # CHECK AVAILABILITY
        # =================================================

        unavailable_seats = []


        for seat in seats:

            if seat.status != "AVAILABLE":

                try:

                    seat_name = (
                        f"{seat.seat.row_label}"
                        f"{seat.seat.seat_number}"
                    )

                except Exception:

                    seat_name = str(
                        seat.id
                    )


                unavailable_seats.append(
                    seat_name
                )


        # =================================================
        # SOMEONE ELSE HAS THE SEAT
        # =================================================

        if unavailable_seats:

            db.session.rollback()

            return jsonify({

                "success": False,

                "message":
                    "These seats are no longer available: "
                    + ", ".join(
                        unavailable_seats
                    )

            }), 409


        # =================================================
        # HOLD FOR 5 MINUTES
        # =================================================

        hold_until = (
            now +
            timedelta(
                minutes=5
            )
        )


        for seat in seats:

            seat.status = "HELD"

            seat.held_by = current_user.id

            seat.hold_until = hold_until


        db.session.flush()


        # =================================================
        # CALCULATE TOTAL
        # =================================================

        total_amount = (
            len(seats)
            * show.price
        )


        # =================================================
        # CREATE BOOKING
        # =================================================

        booking = Booking(

            user_id=current_user.id,

            show_id=show.id,

            total_amount=total_amount,

            booking_status="PENDING",

            payment_done=False,

            payment_status="PENDING"

        )


        db.session.add(
            booking
        )


        db.session.flush()


        # =================================================
        # CREATE BOOKING SEAT RECORDS
        # =================================================

        for seat in seats:

            booking_seat = BookingSeat(

                booking_id=booking.id,

                show_seat_id=seat.id

            )

            db.session.add(
                booking_seat
            )


        db.session.flush()


        # =================================================
        # CREATE PAYMENT URL BEFORE COMMIT
        # =================================================

        payment_url = url_for(

            "payment.payment_page",

            booking_id=booking.id

        )


        # =================================================
        # COMMIT EVERYTHING
        # =================================================

        db.session.commit()


        # =================================================
        # SUCCESS RESPONSE
        # =================================================

        return jsonify({

            "success": True,

            "message":
                "Seats held successfully.",

            "booking_id":
                booking.id,

            "redirect_url":
                payment_url

        }), 200


    except Exception as e:

        db.session.rollback()


        print(
            "================================"
        )

        print(
            "HOLD SEAT ERROR:"
        )

        print(
            repr(e)
        )

        print(
            "================================"
        )


        return jsonify({

            "success": False,

            "message":
                "Unable to hold seats. "
                "Please try again."

        }), 500


# =========================================================
# CANCEL / RELEASE HELD SEATS
# =========================================================

@booking_bp.route(
    "/cancel/<int:booking_id>",
    methods=["POST"]
)
@login_required
def cancel_booking(booking_id):

    booking = Booking.query.get_or_404(
        booking_id
    )


    # =====================================================
    # SECURITY
    # =====================================================

    if booking.user_id != current_user.id:

        return "Unauthorized", 403


    try:

        # =================================================
        # RELEASE SEATS
        # =================================================

        for booking_seat in booking.booking_seats:

            show_seat = (
                booking_seat.show_seat
            )


            if (
                show_seat.held_by
                == current_user.id
                and show_seat.status
                == "HELD"
            ):

                show_seat.status = "AVAILABLE"

                show_seat.held_by = None

                show_seat.hold_until = None


        # =================================================
        # UPDATE BOOKING
        # =================================================

        booking.booking_status = (
            "CANCELLED"
        )

        booking.payment_done = False

        booking.payment_status = (
            "CANCELLED"
        )


        db.session.commit()


        flash(
            "Booking cancelled successfully."
        )


        return redirect(
            url_for(
                "movie.movies"
            )
        )


    except Exception as e:

        db.session.rollback()


        print(
            "CANCEL BOOKING ERROR:",
            repr(e)
        )


        flash(
            "Unable to cancel booking."
        )


        return redirect(
            url_for(
                "booking.history"
            )
        )


# =========================================================
# BOOKING HISTORY
# =========================================================

@booking_bp.route(
    "/history"
)
@login_required
def history():

    bookings = (
        Booking.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Booking.created_at.desc()
        )
        .all()
    )


    return render_template(

        "booking/history.html",

        bookings=bookings

    )


# =========================================================
# BOOKING SUCCESS PAGE
# =========================================================

@booking_bp.route(
    "/success/<int:booking_id>"
)
@login_required
def success(booking_id):

    booking = Booking.query.get_or_404(
        booking_id
    )


    # =====================================================
    # SECURITY
    # =====================================================

    if booking.user_id != current_user.id:

        return "Unauthorized", 403


    # =====================================================
    # GET SHOW AND MOVIE
    # =====================================================

    show = booking.show

    movie = show.movie


    # =====================================================
    # GET SEAT NAMES
    # =====================================================

    seat_names = []


    for booking_seat in booking.booking_seats:

        show_seat = (
            booking_seat.show_seat
        )


        seat = show_seat.seat


        seat_names.append(

            f"{seat.row_label}"
            f"{seat.seat_number}"

        )


    seats = ", ".join(
        seat_names
    )


    # =====================================================
    # SUCCESS PAGE
    # =====================================================

    return render_template(

        "booking/success.html",

        booking=booking,

        show=show,

        movie=movie,

        seats=seats

    )


# =========================================================
# DEVELOPMENT ONLY
# RESET ALL HELD SEATS
# =========================================================

@booking_bp.route(
    "/reset-held"
)
@login_required
def reset_held():

    try:

        held_seats = (
            ShowSeat.query
            .filter_by(
                status="HELD"
            )
            .all()
        )


        count = 0


        for seat in held_seats:

            seat.status = "AVAILABLE"

            seat.held_by = None

            seat.hold_until = None

            count += 1


        # Also cancel pending bookings
        pending_bookings = (
            Booking.query
            .filter_by(
                booking_status="PENDING"
            )
            .all()
        )


        for booking in pending_bookings:

            booking.booking_status = (
                "CANCELLED"
            )

            booking.payment_done = False

            booking.payment_status = (
                "CANCELLED"
            )


        db.session.commit()


        return (
            f"Released {count} held seats."
        )


    except Exception as e:

        db.session.rollback()


        return (
            "Error while resetting seats: "
            + str(e)
        ), 500