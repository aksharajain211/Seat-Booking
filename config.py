import os


class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "cinebook-development-secret"
    )

    SQLALCHEMY_DATABASE_URI = "sqlite:///cinebook.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False