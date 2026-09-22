from app import db


class Seat(db.Model):

    __tablename__ = "seats"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    screen_id = db.Column(
        db.Integer,
        db.ForeignKey("screens.id"),
        nullable=False
    )

    row_label = db.Column(
        db.String(5),
        nullable=False
    )

    seat_number = db.Column(
        db.Integer,
        nullable=False
    )

    seat_type = db.Column(
        db.String(30),
        default="NORMAL"
    )


class ShowSeat(db.Model):

    __tablename__ = "show_seats"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    show_id = db.Column(
        db.Integer,
        db.ForeignKey("shows.id"),
        nullable=False
    )

    seat_id = db.Column(
        db.Integer,
        db.ForeignKey("seats.id"),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="AVAILABLE",
        nullable=False
    )

    held_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    hold_until = db.Column(
        db.DateTime,
        nullable=True
    )

    # Relationship with Seat
    seat = db.relationship(
        "Seat",
        backref="show_seats"
    )

    # Unique seat for every show
    __table_args__ = (
        db.UniqueConstraint(
            "show_id",
            "seat_id",
            name="unique_show_seat"
        ),
    )