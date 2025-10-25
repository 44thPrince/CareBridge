import psycopg2
from psycopg2.extras import DictCursor
from contextlib import contextmanager

DB_NAME = "carebridgedb"   # changed from apt_manager
DB_USER = "postgres"       # update if you use a different user
DB_PASSWORD = "yourpassword"  # replace with your real password
DB_HOST = "localhost"
DB_PORT = "5432"

@contextmanager
def _database_connect():
    """Context manager for safe database connections."""
    connection = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    try:
        with connection:
            yield connection
    finally:
        connection.close()


class DatabasePersistence:
    """Handles direct queries to the database."""

    def find_user_by_username(self, username):
        with _database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE username = %s", (username,))
                return cur.fetchone()

    def insert_client(self, full_name, phone_number, date_of_birth, address, caretaker_id=None):
        with _database_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO clients (full_name, phone_number, date_of_birth, address, caretaker_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                """, (full_name, phone_number, date_of_birth, address, caretaker_id))
                return cur.fetchone()[0]

    def insert_caretaker(self, full_name, phone_number, date_of_birth):
        with _database_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO caretakers (full_name, phone_number, date_of_birth)
                    VALUES (%s, %s, %s)
                    RETURNING id;
                """, (full_name, phone_number, date_of_birth))
                return cur.fetchone()[0]
