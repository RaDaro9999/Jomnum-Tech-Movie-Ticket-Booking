from database import init_database
from db_operations import CinemaDB
from models import Movie, ThreeDMovie, VIPMovie
from exceptions import CinemaSystemError, SeatTakenError


def print_menu():
    print("\n===== Cinema Menu =====")
    print("1. Add standard movie")
    print("2. Add 3D movie")
    print("3. Add VIP movie")
    print("4. Add showtime")
    print("5. Show all movies")
    print("6. Show seat map")
    print("7. Book ticket")
    print("8. Cancel ticket")
    print("9. Show total sales")
    print("10. Exit")


def main():
    # set up database and tables on startup
    init_database()
    db = CinemaDB()

    while True:
        print_menu()
        choice_str = input("Enter your choice: ").strip()

        try:
            choice = int(choice_str)
        except ValueError:
            print("Invalid input. Please enter a number from 1 to 10.")
            continue

        if choice == 10:
            print("Thank you for using the Cinema Booking System. Goodbye!")
            break

        try:
            match choice:
                case 1:
                    movie_id = input("Enter movie ID: ").strip()
                    title = input("Enter movie title: ").strip()
                    duration = int(input("Enter duration (minutes): ").strip())
                    price = float(input("Enter base price: ").strip())

                    movie = Movie(title, movie_id, duration, price)
                    db.add_movie(movie)
                    print(f"Standard movie '{title}' added successfully.")

                case 2:
                    movie_id = input("Enter movie ID: ").strip()
                    title = input("Enter movie title: ").strip()
                    duration = int(input("Enter duration (minutes): ").strip())
                    price = float(input("Enter base price: ").strip())
                    glasses_fee = float(input("Enter 3D glasses fee: ").strip())

                    movie = ThreeDMovie(title, movie_id, duration, price, glasses_fee)
                    db.add_movie(movie)
                    print(f"3D movie '{title}' added successfully.")

                case 3:
                    movie_id = input("Enter movie ID: ").strip()
                    title = input("Enter movie title: ").strip()
                    duration = int(input("Enter duration (minutes): ").strip())
                    price = float(input("Enter base price: ").strip())
                    rate = float(input("Enter service charge rate (e.g. 0.20 or 20): ").strip())

                    movie = VIPMovie(title, movie_id, duration, price, rate)
                    db.add_movie(movie)
                    print(f"VIP movie '{title}' added successfully.")

                case 4:
                    showtime_id = input("Enter showtime ID: ").strip()
                    movie_id = input("Enter movie ID: ").strip()
                    time_str = input("Enter screening time (e.g. 18:30): ").strip()

                    db.add_showtime(showtime_id, movie_id, time_str)
                    print(f"Showtime '{showtime_id}' added successfully.")

                case 5:
                    db.show_all_movies()

                case 6:
                    showtime_id = input("Enter showtime ID: ").strip()
                    db.show_seat_map(showtime_id)

                case 7:
                    customer_name = input("Enter customer name: ").strip()
                    showtime_id = input("Enter showtime ID: ").strip()
                    seat_label = input("Enter seat label: ").strip().upper()

                    ticket = db.book_ticket(customer_name, showtime_id, seat_label)
                    if ticket:
                        print("\nBooking successful!")
                        ticket.display_info()

                case 8:
                    ticket_id = input("Enter ticket ID to cancel: ").strip().upper()
                    db.cancel_ticket(ticket_id)
                    print(f"Ticket {ticket_id} has been cancelled.")

                case 9:
                    total = db.get_total_sales()
                    print(f"\nTotal sales: ${total:.2f}")

                case _:
                    print("Invalid choice. Please choose between 1 and 10.")

        except ValueError:
            print("\nInvalid number format. Please enter valid numbers for duration and price.")
        except SeatTakenError as err:
            print(f"\n{err}")
        except CinemaSystemError as err:
            print(f"\nError: {err}")
        except Exception as err:
            print(f"\nUnexpected error: {err}")


if __name__ == "__main__":
    main()