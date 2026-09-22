from app import db


class Show(db.Model):

    __tablename__ = "shows"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    movie_id = db.Column(
        db.Integer,
        db.ForeignKey("movies.id"),
        nullable=False
    )

    screen_id = db.Column(
        db.Integer,
        db.ForeignKey("screens.id"),
        nullable=False
    )

    start_time = db.Column(
        db.DateTime,
        nullable=False
    )

    end_time = db.Column(
        db.DateTime,
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    movie = db.relationship(
        "Movie",
        backref="shows"
    )

    screen = db.relationship(
        "Screen",
        backref="shows"
    )