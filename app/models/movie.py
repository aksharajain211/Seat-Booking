from app import db


class Movie(db.Model):

    __tablename__ = "movies"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    language = db.Column(
        db.String(50)
    )

    genre = db.Column(
        db.String(100)
    )

    duration = db.Column(
        db.Integer
    )

    rating = db.Column(
        db.Float
    )

    poster_url = db.Column(
        db.String(500)
    )