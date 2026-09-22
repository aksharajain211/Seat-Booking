from datetime import datetime, timedelta

from app import create_app, db

from app.models.movie import Movie
from app.models.theatre import Theatre
from app.models.screen import Screen
from app.models.seat import Seat, ShowSeat
from app.models.show import Show


app = create_app()


with app.app_context():

    # -----------------------------
    # CLEAR OLD DATA
    # -----------------------------

    ShowSeat.query.delete()
    Show.query.delete()
    Seat.query.delete()
    Screen.query.delete()
    Theatre.query.delete()
    Movie.query.delete()

    db.session.commit()

    # -----------------------------
    # MOVIES
    # -----------------------------

    movie1 = Movie(
        title="Avengers: Endgame",
        description="The Avengers fight their final battle.",
        duration=181,
        language="English",
        genre="Action",
        rating=8.4,
        poster_url="https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg"
    )

    movie2 = Movie(
        title="Interstellar",
        description="A team travels through space to find a new home for humanity.",
        duration=169,
        language="English",
        genre="Sci-Fi",
        rating=8.7,
        poster_url="https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg"
    )

    movie3 = Movie(
        title="3 Idiots",
        description="Three friends experience college life and discover their passion.",
        duration=170,
        language="Hindi",
        genre="Comedy",
        rating=8.4,
        poster_url="https://image.tmdb.org/t/p/w500/66A9MqXOyVFCssoloscwG9H1h4I.jpg"
    )

    db.session.add_all([
        movie1,
        movie2,
        movie3
    ])

    db.session.commit()

    # -----------------------------
    # THEATRE
    # -----------------------------

    theatre = Theatre(
        name="CineBook Multiplex",
        location="Jaipur, Rajasthan"
    )

    db.session.add(theatre)
    db.session.commit()

    # -----------------------------
    # SCREEN
    # -----------------------------

    screen = Screen(
        theatre_id=theatre.id,
        name="Screen 1"
    )

    db.session.add(screen)
    db.session.commit()

    # -----------------------------
    # SEATS
    # -----------------------------

    seats = []

    for row in ["A", "B", "C", "D", "E"]:

        for number in range(1, 11):

            seat = Seat(
                screen_id=screen.id,
                row_label=row,
                seat_number=number,
                seat_type="NORMAL"
            )

            seats.append(seat)

    db.session.add_all(seats)
    db.session.commit()

    # -----------------------------
    # SHOWS
    # -----------------------------

    now = datetime.now()

    show1 = Show(
        movie_id=movie1.id,
        screen_id=screen.id,
        start_time=now + timedelta(hours=2),
        end_time=now + timedelta(hours=5),
        price=250
    )

    show2 = Show(
        movie_id=movie2.id,
        screen_id=screen.id,
        start_time=now + timedelta(hours=6),
        end_time=now + timedelta(hours=9),
        price=300
    )

    show3 = Show(
        movie_id=movie3.id,
        screen_id=screen.id,
        start_time=now + timedelta(days=1, hours=2),
        end_time=now + timedelta(days=1, hours=5),
        price=200
    )

    db.session.add_all([
        show1,
        show2,
        show3
    ])

    db.session.commit()

    # -----------------------------
    # CREATE SHOW SEATS
    # -----------------------------

    shows = [
        show1,
        show2,
        show3
    ]

    for show in shows:

        for seat in seats:

            show_seat = ShowSeat(
                show_id=show.id,
                seat_id=seat.id,
                status="AVAILABLE"
            )

            db.session.add(show_seat)

    db.session.commit()

    print()
    print("================================")
    print("🎬 CineBook database seeded!")
    print("================================")
    print()
    print("Movies:", Movie.query.count())
    print("Theatres:", Theatre.query.count())
    print("Screens:", Screen.query.count())
    print("Seats:", Seat.query.count())
    print("Shows:", Show.query.count())
    print("Show Seats:", ShowSeat.query.count())
    print()