from datetime import datetime
import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    url_for
)

from flask_login import (
    login_required,
    current_user
)

from app import db

from app.models.booking import Booking
from app.models.seat import ShowSeat


payment_bp = Blueprint(
    "payment",
    __name__,
    url_prefix="/payment"
)


# =========================================================
# PAYMENT PAGE
# =========================================================

@payment_bp.route("/<int:booking_id>")
@login_required
def payment_page(booking_id):

    booking = Booking.query.get_or_404(booking_id)


    # -----------------------------------------------------
    # Security check
    # -----------------------------------------------------

    if booking.user_id != current_user.id:

        return "Unauthorized", 403


    # -----------------------------------------------------
    # Booking must still be pending
    # -----------------------------------------------------

    if booking.booking_status != "PENDING":

        return redirect(
            url_for(
                "booking.success",
                booking_id=booking.id
            )
        )


    # -----------------------------------------------------
    # Get booking seats
    # -----------------------------------------------------

    booking_seats = booking.booking_seats


    if not booking_seats:

        return "No seats found for this booking.", 400


    # -----------------------------------------------------
    # Check hold time
    # -----------------------------------------------------

    now = datetime.utcnow()


    hold_until = None


    for booking_seat in booking_seats:

        show_seat = booking_seat.show_seat


        if (
            show_seat.status != "HELD"
            or show_seat.held_by != current_user.id
        ):

            return (
                "Seat hold is no longer valid.",
                400
            )


        if (
            show_seat.hold_until is None
            or show_seat.hold_until <= now
        ):

            # Release expired seat

            show_seat.status = "AVAILABLE"
            show_seat.held_by = None
            show_seat.hold_until = None


            booking.booking_status = "CANCELLED"
            booking.payment_status = "CANCELLED"
            booking.payment_done = False


            db.session.commit()


            return (
                "Your seat hold has expired. "
                "Please select the seats again.",
                400
            )


        # Find latest hold time

        if (
            hold_until is None
            or show_seat.hold_until > hold_until
        ):

            hold_until = show_seat.hold_until


    # -----------------------------------------------------
    # Seat names
    # -----------------------------------------------------

    seat_names = []


    for booking_seat in booking_seats:

        seat = booking_seat.show_seat.seat

        seat_names.append(
            f"{seat.row_label}{seat.seat_number}"
        )


    seats = ", ".join(seat_names)


    # -----------------------------------------------------
    # Show
    # -----------------------------------------------------

    show = booking.show


    # -----------------------------------------------------
    # Movie
    # -----------------------------------------------------

    movie = show.movie


    return render_template(
        "booking/payment.html",

        booking=booking,

        show=show,

        movie=movie,

        seats=seats,

        hold_until=hold_until
    )


# =========================================================
# CONFIRM PAYMENT
# =========================================================

@payment_bp.route(
    "/confirm/<int:booking_id>",
    methods=["POST"]
)
@login_required
def confirm_payment(booking_id):

    booking = Booking.query.get_or_404(booking_id)


    # -----------------------------------------------------
    # Security check
    # -----------------------------------------------------

    if booking.user_id != current_user.id:

        return jsonify({
            "success": False,
            "message": "Unauthorized booking."
        }), 403


    # -----------------------------------------------------
    # Check booking status
    # -----------------------------------------------------

    if booking.booking_status != "PENDING":

        return jsonify({
            "success": False,
            "message": "This booking is no longer pending."
        }), 400


    # -----------------------------------------------------
    # Get selected payment method
    # -----------------------------------------------------

    data = request.get_json(silent=True) or {}

    payment_method = data.get(
        "payment_method",
        "DEMO"
    )


    # -----------------------------------------------------
    # Get booking seats
    # -----------------------------------------------------

    booking_seats = booking.booking_seats


    if not booking_seats:

        return jsonify({
            "success": False,
            "message": "No seats found for this booking."
        }), 400


    # -----------------------------------------------------
    # Check seat holds
    # -----------------------------------------------------

    now = datetime.utcnow()


    for booking_seat in booking_seats:

        show_seat = booking_seat.show_seat


        # Seat must still be held by this user

        if (
            show_seat.status != "HELD"
            or show_seat.held_by != current_user.id
        ):

            return jsonify({
                "success": False,
                "message":
                    "One or more seats are no longer held."
            }), 409


        # Hold must not be expired

        if (
            show_seat.hold_until is None
            or show_seat.hold_until <= now
        ):

            # Release expired seat

            show_seat.status = "AVAILABLE"
            show_seat.held_by = None
            show_seat.hold_until = None


            booking.booking_status = "CANCELLED"
            booking.payment_status = "CANCELLED"
            booking.payment_done = False


            db.session.commit()


            return jsonify({
                "success": False,
                "message":
                    "Your seat hold has expired. "
                    "Please select the seats again."
            }), 400


    # -----------------------------------------------------
    # DEMO PAYMENT
    # -----------------------------------------------------

    # No real payment gateway is used.

    transaction_id = (
        "DEMO-"
        + uuid.uuid4().hex[:12].upper()
    )


    # -----------------------------------------------------
    # Mark payment successful
    # -----------------------------------------------------

    booking.payment_done = True

    booking.payment_status = "SUCCESS"

    booking.booking_status = "CONFIRMED"

    booking.transaction_id = transaction_id


    # -----------------------------------------------------
    # Mark seats BOOKED
    # -----------------------------------------------------

    for booking_seat in booking_seats:

        show_seat = booking_seat.show_seat


        show_seat.status = "BOOKED"

        show_seat.held_by = None

        show_seat.hold_until = None


    # -----------------------------------------------------
    # Save everything
    # -----------------------------------------------------

    db.session.commit()


    # -----------------------------------------------------
    # Success response
    # -----------------------------------------------------

    return jsonify({

        "success": True,

        "message":
            "Payment successful.",

        "payment_method":
            payment_method,

        "transaction_id":
            transaction_id,

        "redirect_url":
            url_for(
                "booking.success",
                booking_id=booking.id
            )

    })


# =========================================================
# CANCEL PAYMENT
# =========================================================

@payment_bp.route(
    "/cancel/<int:booking_id>",
    methods=["POST"]
)
@login_required
def cancel_payment(booking_id):

    booking = Booking.query.get_or_404(booking_id)


    # Security check

    if booking.user_id != current_user.id:

        return jsonify({
            "success": False,
            "message": "Unauthorized booking."
        }), 403


    # -----------------------------------------------------
    # Release seats
    # -----------------------------------------------------

    for booking_seat in booking.booking_seats:

        show_seat = booking_seat.show_seat


        if (
            show_seat.status == "HELD"
            and show_seat.held_by == current_user.id
        ):

            show_seat.status = "AVAILABLE"

            show_seat.held_by = None

            show_seat.hold_until = None


    # -----------------------------------------------------
    # Cancel booking
    # -----------------------------------------------------

    booking.booking_status = "CANCELLED"

    booking.payment_status = "CANCELLED"

    booking.payment_done = False


    db.session.commit()


    return jsonify({

        "success": True,

        "redirect_url":
            url_for("movie.movies")

    })