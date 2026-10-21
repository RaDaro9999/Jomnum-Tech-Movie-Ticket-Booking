# Custom exceptions for the movie ticket booking system

class CinemaSystemError(Exception):
    pass

class SeatTakenError(CinemaSystemError):
    pass

class SeatNotFoundError(CinemaSystemError):
    pass

class MovieNotFoundError(CinemaSystemError):
    pass

class ShowtimeNotFoundError(CinemaSystemError):
    pass

class TicketNotFoundError(CinemaSystemError):
    pass

class DuplicateMovieError(CinemaSystemError):
    pass

class InvalidInputError(CinemaSystemError):
    pass