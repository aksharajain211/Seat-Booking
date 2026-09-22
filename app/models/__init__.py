def import_models():

    from app.models.user import User
    from app.models.movie import Movie
    from app.models.theatre import Theatre
    from app.models.screen import Screen
    from app.models.seat import Seat, ShowSeat
    from app.models.show import Show
    from app.models.booking import Booking, BookingSeat
    from app.models.payment import Payment