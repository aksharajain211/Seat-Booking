from app import db


class Theatre(db.Model):

    __tablename__ = "theatres"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(200),
        nullable=False
    )

    location = db.Column(
        db.String(300),
        nullable=False
    )