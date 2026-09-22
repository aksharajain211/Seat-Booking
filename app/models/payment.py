from datetime import datetime

from app import db


class Payment(db.Model):

    __tablename__ = "payments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id"),
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    payment_done = db.Column(
        db.Boolean,
        default=False
    )

    payment_status = db.Column(
        db.String(20),
        default="PENDING"
    )

    transaction_id = db.Column(
        db.String(200)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )