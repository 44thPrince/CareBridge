import psycopg2
from psycopg2.extras import DictCursor
from contextlib import contextmanager

DB_NAME = "carebridgedb"   # changed from apt_manager
DB_USER = "postgres"   # update if you use a different user
DB_PASSWORD = "RobinHood2025!"  # replace with your real password
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

    def insert_client(self, full_name, phone_number, date_of_birth, address, emergency_contact_name=None, 
                     emergency_contact_phone=None, medical_conditions=None, special_instructions=None, user_id=None):
        with _database_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO clients (full_name, phone_number, date_of_birth, address, 
                                        emergency_contact_name, emergency_contact_phone, 
                                        medical_conditions, special_instructions, user_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (full_name, phone_number, date_of_birth, address, emergency_contact_name,
                     emergency_contact_phone, medical_conditions, special_instructions, user_id))
                return cur.fetchone()[0]

    def insert_caretaker(self, full_name, phone_number, date_of_birth, email=None, address=None,
                        city=None, state=None, zip_code=None, bio=None, years_experience=0,
                        hourly_rate=None, availability=None, certifications=None, languages=None, user_id=None):
        with _database_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO caretakers (full_name, phone_number, date_of_birth, email, address,
                                           city, state, zip_code, bio, years_experience, hourly_rate,
                                           availability, certifications, languages, user_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (full_name, phone_number, date_of_birth, email, address, city, state, zip_code,
                     bio, years_experience, hourly_rate, availability, certifications, languages, user_id))
                return cur.fetchone()[0]

    def get_all_caretakers(self):
        """Get all caretakers with their details."""
        with _database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT * FROM caretakers ORDER BY created_at DESC")
                return cur.fetchall()

    def get_all_clients(self):
        """Get all clients with their details."""
        with _database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT * FROM clients ORDER BY created_at DESC")
                return cur.fetchall()

    def get_caretaker_by_id(self, caretaker_id):
        """Get a specific caretaker by ID."""
        with _database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT * FROM caretakers WHERE id = %s", (caretaker_id,))
                return cur.fetchone()

    def get_caretaker_adls(self, caretaker_id):
        """Get all ADL services for a specific caretaker."""
        with _database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT * FROM caretaker_adls 
                    WHERE caretaker_id = %s AND is_available = TRUE
                    ORDER BY service_type
                """, (caretaker_id,))
                return cur.fetchall()

    def get_all_adl_services(self):
        """Get all available ADL service types."""
        with _database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT * FROM adl_service_types 
                    ORDER BY display_order, category
                """)
                return cur.fetchall()

    def get_adls_by_category(self, category):
        """Get ADL services filtered by category."""
        with _database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT * FROM adl_service_types 
                    WHERE category = %s
                    ORDER BY display_order
                """, (category,))
                return cur.fetchall()

    def search_caretakers_by_adl(self, service_type):
        """Find caretakers who offer a specific ADL service."""
        with _database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT c.* 
                    FROM caretakers c
                    JOIN caretaker_adls ca ON c.id = ca.caretaker_id
                    WHERE ca.service_type = %s AND ca.is_available = TRUE
                    ORDER BY c.full_name
                """, (service_type,))
                return cur.fetchall()

    def add_caretaker_adl(self, caretaker_id, service_type, notes=None):
        """Add an ADL service capability to a caretaker."""
        with _database_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO caretaker_adls (caretaker_id, service_type, notes)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (caretaker_id, service_type) 
                    DO UPDATE SET is_available = TRUE, notes = %s
                """, (caretaker_id, service_type, notes, notes))

    def remove_caretaker_adl(self, caretaker_id, service_type):
        """Mark an ADL service as unavailable for a caretaker."""
        with _database_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE caretaker_adls 
                    SET is_available = FALSE 
                    WHERE caretaker_id = %s AND service_type = %s
                """, (caretaker_id, service_type))
