from datetime import datetime

from app import db


class Booking(db.Model):

    __tablename__ = "bookings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    show_id = db.Column(
        db.Integer,
        db.ForeignKey("shows.id"),
        nullable=False
    )

    total_amount = db.Column(
        db.Float,
        nullable=False
    )

    booking_status = db.Column(
        db.String(30),
        default="PENDING",
        nullable=False
    )

    # =========================================
    # MOCK PAYMENT
    # =========================================

    payment_done = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    payment_status = db.Column(
        db.String(30),
        default="PENDING",
        nullable=False
    )

    transaction_id = db.Column(
        db.String(100),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # =========================================
    # RELATIONSHIPS
    # =========================================

    user = db.relationship(
        "User",
        backref="bookings"
    )

    show = db.relationship(
        "Show",
        backref="bookings"
    )

    booking_seats = db.relationship(
        "BookingSeat",
        backref="booking",
        cascade="all, delete-orphan"
    )


class BookingSeat(db.Model):

    __tablename__ = "booking_seats"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id"),
        nullable=False
    )

    show_seat_id = db.Column(
        db.Integer,
        db.ForeignKey("show_seats.id"),
        nullable=False
    )

    show_seat = db.relationship(
        "ShowSeat",
        backref="booking_seats"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "booking_id",
            "show_seat_id",
            name="unique_booking_seat"
        ),
    )