from app import db


class Screen(db.Model):

    __tablename__ = "screens"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    theatre_id = db.Column(
        db.Integer,
        db.ForeignKey("theatres.id"),
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )