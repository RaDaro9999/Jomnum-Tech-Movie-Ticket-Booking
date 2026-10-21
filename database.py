import mysql.connector
from mysql.connector import Error

# Database connection configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root1234",
    "database": "cinema_db"
}

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as err:
        print(f"Database connection error: {err}")
        return None

def init_database():
    server_conn = None
    conn = None
    try:
        # connect to MySQL server to create database if it does not exist
        server_conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        cursor = server_conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']};")
        cursor.close()
        server_conn.close()

        # connect to cinema_db and create tables
        conn = get_db_connection()
        if not conn:
            return

        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                movie_id VARCHAR(20) PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                movie_type ENUM('Standard', '3D', 'VIP') NOT NULL,
                duration_minutes INT NOT NULL,
                base_price DECIMAL(10, 2) NOT NULL,
                glasses_fee DECIMAL(10, 2) DEFAULT 0.00,
                service_charge_rate DECIMAL(5, 2) DEFAULT 0.00
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS showtimes (
                showtime_id VARCHAR(20) PRIMARY KEY,
                movie_id VARCHAR(20) NOT NULL,
                screening_time VARCHAR(20) NOT NULL,
                FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS seats (
                seat_id INT AUTO_INCREMENT PRIMARY KEY,
                showtime_id VARCHAR(20) NOT NULL,
                seat_label VARCHAR(10) NOT NULL,
                is_taken BOOLEAN NOT NULL DEFAULT FALSE,
                UNIQUE KEY uq_showtime_seat (showtime_id, seat_label),
                FOREIGN KEY (showtime_id) REFERENCES showtimes(showtime_id) ON DELETE CASCADE
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id VARCHAR(20) PRIMARY KEY,
                customer_name VARCHAR(100) NOT NULL,
                showtime_id VARCHAR(20) NOT NULL,
                seat_label VARCHAR(10) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (showtime_id) REFERENCES showtimes(showtime_id) ON DELETE CASCADE
            );
        """)

        conn.commit()
        cursor.close()

    except Error as err:
        print(f"Error initializing database: {err}")
    finally:
        if server_conn and server_conn.is_connected():
            server_conn.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    print("Testing connection and setting up database")
    init_database()
    print("Database setup complete!")