from exceptions import (
    CinemaSystemError,
    SeatTakenError,
    SeatNotFoundError,
    MovieNotFoundError,
    ShowtimeNotFoundError,
    TicketNotFoundError,
    DuplicateMovieError,
    InvalidInputError
)

# Base class for Movie
class Movie:
    def __init__(self, title, movie_id, duration_minutes, base_price):
        if duration_minutes <= 0:
            raise InvalidInputError("Duration must be greater than 0.")
        if base_price < 0:
            raise InvalidInputError("Base price cannot be negative.")

        self.title = title
        self.movie_id = movie_id
        self.duration_minutes = int(duration_minutes)
        self.base_price = float(base_price)

    def get_movie_type(self):
        return "Standard"

    def get_ticket_price(self):
        return self.base_price

    def display_info(self):
        print(f"Movie ID: {self.movie_id}")
        print(f"Title: {self.title}")
        print(f"Type: {self.get_movie_type()}")
        print(f"Duration: {self.duration_minutes} mins")
        print(f"Ticket Price: ${self.get_ticket_price():.2f}")


# Child class for 3D Movie
class ThreeDMovie(Movie):
    def __init__(self, title, movie_id, duration_minutes, base_price, glasses_fee):
        super().__init__(title, movie_id, duration_minutes, base_price)
        if glasses_fee < 0:
            raise InvalidInputError("Glasses fee cannot be negative.")
        self.glasses_fee = float(glasses_fee)

    def get_movie_type(self):
        return "3D"

    def get_ticket_price(self):
        return self.base_price + self.glasses_fee

    def display_info(self):
        super().display_info()
        print(f"Glasses Fee: ${self.glasses_fee:.2f}")


# Child class for VIP Movie
class VIPMovie(Movie):
    def __init__(self, title, movie_id, duration_minutes, base_price, service_charge_rate):
        super().__init__(title, movie_id, duration_minutes, base_price)
        if service_charge_rate < 0:
            raise InvalidInputError("Service charge rate cannot be negative.")
        # convert 20 to 0.20 if entered as percentage
        if service_charge_rate > 1:
            service_charge_rate = service_charge_rate / 100
        self.service_charge_rate = float(service_charge_rate)

    def get_movie_type(self):
        return "VIP"

    def get_ticket_price(self):
        return self.base_price + (self.base_price * self.service_charge_rate)

    def display_info(self):
        super().display_info()
        print(f"Service Charge: {self.service_charge_rate * 100:.0f}%")


# Seat class with encapsulation
class Seat:
    def __init__(self, seat_label):
        self.seat_label = seat_label
        self.__is_taken = False

    def is_taken(self):
        return self.__is_taken

    def reserve(self):
        if self.__is_taken:
            raise SeatTakenError(f"Sorry, seat {self.seat_label} is already taken. Please choose another seat.")
        self.__is_taken = True

    def release(self):
        self.__is_taken = False


# Showtime class
class Showtime:
    def __init__(self, showtime_id, movie, time):
        self.showtime_id = showtime_id
        self.movie = movie
        self.time = time
        self.seats = {}

        # create 15 seats from A1 to C5
        for row in ['A', 'B', 'C']:
            for col in range(1, 6):
                label = f"{row}{col}"
                self.seats[label] = Seat(label)

    def get_seat(self, seat_label):
        if seat_label not in self.seats:
            raise SeatNotFoundError(f"Seat {seat_label} does not exist.")
        return self.seats[seat_label]

    def count_free_seats(self):
        free_count = 0
        for seat in self.seats.values():
            if not seat.is_taken():
                free_count += 1
        return free_count

    def show_seat_map(self):
        print(f"\n--- Seat Map: {self.movie.title} ({self.time}) ---")
        print("    1   2   3   4   5")
        for row in ['A', 'B', 'C']:
            line = f"{row} "
            for col in range(1, 6):
                label = f"{row}{col}"
                if self.seats[label].is_taken():
                    line += " [X]"
                else:
                    line += " [ ]"
            print(line)
        print(f"Free seats: {self.count_free_seats()}")


# Ticket class
class Ticket:
    def __init__(self, ticket_id, customer_name, showtime, seat_label, price):
        self.ticket_id = ticket_id
        self.customer_name = customer_name
        self.showtime = showtime
        self.seat_label = seat_label
        self.price = float(price)

    def display_info(self):
        print(f"Ticket ID: {self.ticket_id}")
        print(f"Customer: {self.customer_name}")
        print(f"Movie: {self.showtime.movie.title} ({self.showtime.movie.get_movie_type()})")
        print(f"Time: {self.showtime.time}")
        print(f"Seat: {self.seat_label}")
        print(f"Price: ${self.price:.2f}")


# Cinema class
class Cinema:
    def __init__(self):
        self.movies = {}
        self.showtimes = {}
        self.tickets = {}
        self.total_sales = 0.0

    def add_movie(self, movie):
        if movie.movie_id in self.movies:
            raise DuplicateMovieError(f"Movie ID {movie.movie_id} already exists.")
        self.movies[movie.movie_id] = movie

    def add_showtime(self, showtime):
        if showtime.showtime_id in self.showtimes:
            raise CinemaSystemError(f"Showtime ID {showtime.showtime_id} already exists.")
        self.showtimes[showtime.showtime_id] = showtime

    def show_all_movies(self):
        if not self.movies:
            print("\nNo movies available.")
            return

        print("\n--- All Movies ---")
        for movie in self.movies.values():
            movie.display_info()
            print("-" * 25)

    def show_showtimes(self):
        if not self.showtimes:
            print("\nNo showtimes available.")
            return

        print("\n--- Showtimes ---")
        for st in self.showtimes.values():
            print(f"Showtime ID: {st.showtime_id} | Movie: {st.movie.title} | Time: {st.time} | Free seats: {st.count_free_seats()}")

    def book_ticket(self, customer_name, showtime_id, seat_label):
        if showtime_id not in self.showtimes:
            raise ShowtimeNotFoundError(f"Showtime ID {showtime_id} not found.")

        showtime = self.showtimes[showtime_id]
        seat = showtime.get_seat(seat_label)
        seat.reserve()

        price = showtime.movie.get_ticket_price()
        self.total_sales += price

        ticket_id = f"T{len(self.tickets) + 1:03d}"
        ticket = Ticket(ticket_id, customer_name, showtime, seat_label, price)
        self.tickets[ticket_id] = ticket
        return ticket

    def cancel_ticket(self, ticket_id):
        if ticket_id not in self.tickets:
            raise TicketNotFoundError(f"Ticket ID {ticket_id} not found.")

        ticket = self.tickets[ticket_id]
        seat = ticket.showtime.get_seat(ticket.seat_label)
        seat.release()

        self.total_sales -= ticket.price
        del self.tickets[ticket_id]
        return True

    def get_total_sales(self):
        return self.total_sales