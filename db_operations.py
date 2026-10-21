from database import get_db_connection
from models import Movie, ThreeDMovie, VIPMovie, Showtime, Ticket
from exceptions import (
    CinemaSystemError,
    SeatTakenError,
    SeatNotFoundError,
    MovieNotFoundError,
    ShowtimeNotFoundError,
    TicketNotFoundError,
    DuplicateMovieError
)

class CinemaDB:
    # helper method to convert database row into a Movie object
    def _build_movie_object(self, row):
        match row['movie_type']:
            case '3D':
                return ThreeDMovie(
                    row['title'],
                    row['movie_id'],
                    row['duration_minutes'],
                    float(row['base_price']),
                    float(row['glasses_fee'])
                )
            case 'VIP':
                return VIPMovie(
                    row['title'],
                    row['movie_id'],
                    row['duration_minutes'],
                    float(row['base_price']),
                    float(row['service_charge_rate'])
                )
            case _:
                return Movie(
                    row['title'],
                    row['movie_id'],
                    row['duration_minutes'],
                    float(row['base_price'])
                )

    def add_movie(self, movie):
        conn = get_db_connection()
        if not conn:
            return

        cursor = conn.cursor()
        try:
            # check if movie_id already exists
            cursor.execute("SELECT movie_id FROM movies WHERE movie_id = %s", (movie.movie_id,))
            if cursor.fetchone():
                raise DuplicateMovieError(f"Movie ID '{movie.movie_id}' already exists.")

            m_type = movie.get_movie_type()
            glasses_fee = 0.0
            service_rate = 0.0

            if isinstance(movie, ThreeDMovie):
                glasses_fee = movie.glasses_fee
            elif isinstance(movie, VIPMovie):
                service_rate = movie.service_charge_rate

            sql = """
                INSERT INTO movies (movie_id, title, movie_type, duration_minutes, base_price, glasses_fee, service_charge_rate)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                movie.movie_id,
                movie.title,
                m_type,
                movie.duration_minutes,
                movie.base_price,
                glasses_fee,
                service_rate
            ))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def add_showtime(self, showtime_id, movie_id, screening_time):
        conn = get_db_connection()
        if not conn:
            return

        cursor = conn.cursor()
        try:
            # check if movie exists
            cursor.execute("SELECT movie_id FROM movies WHERE movie_id = %s", (movie_id,))
            if not cursor.fetchone():
                raise MovieNotFoundError(f"Movie ID '{movie_id}' not found.")

            # check if showtime_id already exists
            cursor.execute("SELECT showtime_id FROM showtimes WHERE showtime_id = %s", (showtime_id,))
            if cursor.fetchone():
                raise CinemaSystemError(f"Showtime ID '{showtime_id}' already exists.")

            cursor.execute(
                "INSERT INTO showtimes (showtime_id, movie_id, screening_time) VALUES (%s, %s, %s)",
                (showtime_id, movie_id, screening_time)
            )

            # create 15 seats from A1 to C5
            seats_data = []
            for row in ['A', 'B', 'C']:
                for col in range(1, 6):
                    seat_label = f"{row}{col}"
                    seats_data.append((showtime_id, seat_label, False))

            cursor.executemany(
                "INSERT INTO seats (showtime_id, seat_label, is_taken) VALUES (%s, %s, %s)",
                seats_data
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def show_all_movies(self):
        conn = get_db_connection()
        if not conn:
            return

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM movies")
            rows = cursor.fetchall()

            if not rows:
                print("\nNo movies found.")
                return

            print("\n--- All Movies ---")
            for row in rows:
                movie_obj = self._build_movie_object(row)
                movie_obj.display_info()
                print("-" * 25)
        finally:
            cursor.close()
            conn.close()

    def show_seat_map(self, showtime_id):
        conn = get_db_connection()
        if not conn:
            return

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT s.showtime_id, s.screening_time, m.*
                FROM showtimes s
                JOIN movies m ON s.movie_id = m.movie_id
                WHERE s.showtime_id = %s
            """, (showtime_id,))
            row = cursor.fetchone()

            if not row:
                raise ShowtimeNotFoundError(f"Showtime ID '{showtime_id}' not found.")

            movie_obj = self._build_movie_object(row)
            showtime_obj = Showtime(row['showtime_id'], movie_obj, row['screening_time'])

            cursor.execute("SELECT seat_label, is_taken FROM seats WHERE showtime_id = %s", (showtime_id,))
            for seat_row in cursor.fetchall():
                if seat_row['is_taken']:
                    showtime_obj.get_seat(seat_row['seat_label']).reserve()

            showtime_obj.show_seat_map()
        finally:
            cursor.close()
            conn.close()

    def book_ticket(self, customer_name, showtime_id, seat_label):
        conn = get_db_connection()
        if not conn:
            return None

        cursor = conn.cursor(dictionary=True)
        try:
            # 1. check showtime and get movie info
            cursor.execute("""
                SELECT s.showtime_id, s.screening_time, m.*
                FROM showtimes s
                JOIN movies m ON s.movie_id = m.movie_id
                WHERE s.showtime_id = %s
            """, (showtime_id,))
            row = cursor.fetchone()

            if not row:
                raise ShowtimeNotFoundError(f"Showtime ID '{showtime_id}' not found.")

            movie_obj = self._build_movie_object(row)
            showtime_obj = Showtime(row['showtime_id'], movie_obj, row['screening_time'])

            # 2. check if seat exists and is available
            cursor.execute(
                "SELECT is_taken FROM seats WHERE showtime_id = %s AND seat_label = %s",
                (showtime_id, seat_label)
            )
            seat_row = cursor.fetchone()

            if not seat_row:
                raise SeatNotFoundError(f"Seat '{seat_label}' does not exist.")

            seat_obj = showtime_obj.get_seat(seat_label)
            if seat_row['is_taken']:
                seat_obj.reserve()
            seat_obj.reserve()

            # 3. calculate ticket price using polymorphism
            final_price = movie_obj.get_ticket_price()

            # 4. generate next ticket ID
            cursor.execute("SELECT ticket_id FROM tickets ORDER BY ticket_id DESC LIMIT 1")
            last_ticket = cursor.fetchone()
            if last_ticket:
                last_num = int(last_ticket['ticket_id'][1:])
                ticket_id = f"T{last_num + 1:03d}"
            else:
                ticket_id = "T001"

            # 5. update seat status and save ticket
            cursor.execute(
                "UPDATE seats SET is_taken = TRUE WHERE showtime_id = %s AND seat_label = %s",
                (showtime_id, seat_label)
            )
            cursor.execute("""
                INSERT INTO tickets (ticket_id, customer_name, showtime_id, seat_label, price)
                VALUES (%s, %s, %s, %s, %s)
            """, (ticket_id, customer_name, showtime_id, seat_label, final_price))

            conn.commit()
            return Ticket(ticket_id, customer_name, showtime_obj, seat_label, final_price)

        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def cancel_ticket(self, ticket_id):
        conn = get_db_connection()
        if not conn:
            return False

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM tickets WHERE ticket_id = %s", (ticket_id,))
            ticket = cursor.fetchone()

            if not ticket:
                raise TicketNotFoundError(f"Ticket ID '{ticket_id}' not found.")

            # release seat and delete ticket record
            cursor.execute(
                "UPDATE seats SET is_taken = FALSE WHERE showtime_id = %s AND seat_label = %s",
                (ticket['showtime_id'], ticket['seat_label'])
            )
            cursor.execute("DELETE FROM tickets WHERE ticket_id = %s", (ticket_id,))
            conn.commit()
            return True

        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def get_total_sales(self):
        conn = get_db_connection()
        if not conn:
            return 0.0

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COALESCE(SUM(price), 0.0) FROM tickets")
            total = cursor.fetchone()[0]
            return float(total)
        finally:
            cursor.close()
            conn.close()