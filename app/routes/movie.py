from flask import Blueprint, render_template, redirect, url_for

from app.models.movie import Movie
from app.models.show import Show


movie_bp = Blueprint(
    "movie",
    __name__,
    url_prefix="/movies"
)


@movie_bp.route("/")
def movies():
    movies = Movie.query.all()

    return render_template(
        "movies/movies.html",
        movies=movies
    )


@movie_bp.route("/movie/<int:movie_id>")
def movie_details(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    shows = (
        Show.query
        .filter_by(movie_id=movie.id)
        .order_by(Show.start_time)
        .all()
    )

    return render_template(
        "movies/movie_details.html",
        movie=movie,
        shows=shows
    )


@movie_bp.route("/home")
def home():
    return redirect(url_for("movie.movies"))