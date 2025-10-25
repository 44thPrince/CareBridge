import psycopg2
from psycopg2.extras import DictCursor
from contextlib import contextmanager
import json
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# Get credentials from environment variables
DB_NAME = os.getenv('DB_NAME', "carebridgedb")
DB_USER = os.getenv('DB_USER', "postgres")
DB_PASSWORD = os.getenv('DB_PASSWORD', "") 
DB_HOST = os.getenv('DB_HOST', "localhost")
DB_PORT = os.getenv('DB_PORT', "5432")

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
                      emergency_contact_phone=None, medical_conditions=None, special_instructions=None):
        with _database_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO clients (full_name, phone_number, date_of_birth, address, 
                                         emergency_contact_name, emergency_contact_phone, 
                                         medical_conditions, special_instructions)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (full_name, phone_number, date_of_birth, address, emergency_contact_name,
                      emergency_contact_phone, medical_conditions, special_instructions))
                return cur.fetchone()[0]

    def insert_caretaker(self, full_name, phone_number, date_of_birth, email=None, address=None,
                         city=None, state=None, zip_code=None, bio=None, years_experience=0,
                         hourly_rate=None, availability=None, certifications=None, languages=None):
        with _database_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO caretakers (full_name, phone_number, date_of_birth, email, address,
                                             city, state, zip_code, bio, years_experience, hourly_rate,
                                             availability, certifications, languages)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (full_name, phone_number, date_of_birth, email, address, city, state, zip_code,
                      bio, years_experience, hourly_rate, availability, certifications, languages))
                return cur.fetchone()[0]

    def get_all_caretakers(self):
        """Get all caretakers with their details."""
        with _database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT * FROM caretakers ORDER BY created_at DESC")
                return cur.fetchall()

    def get_caretaker_by_id(self, caretaker_id):
        """Get a specific caretaker by ID."""
        with _database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT * FROM caretakers WHERE id = %s", (caretaker_id,))
                return cur.fetchone()

    def get_patient_by_id(self, patient_id):
        """
        Get a specific patient by ID, augmenting with AI agent-required fields
        for the demo profile (Patient 1).
        """
        with _database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT * FROM clients WHERE id = %s", (patient_id,))
                client_data = cur.fetchone()
        
        if not client_data:
            return None

        # --- DEMO DATA INTEGRATION for AI AGENT (Patient 1: Alice Johnson) ---
        
        if client_data['id'] == 1:
            return {
                **dict(client_data),
                'full_name': client_data['full_name'],
                'patient_city': 'Orlando',
                'patient_state': 'FL',
                'language_preference': 'English',
                'required_care_level': 'Moderate (ADL/IADL support)',
                'level_of_mobility': 'Walks with cane, needs assistance for transfers',
                'cognitive_status': 'Early-stage Dementia',
                'fall_risk_level': 'Moderate',
                'specific_medical_conditions': ['Dementia', 'Mild Arthritis'],
                'required_services': ['Bathing & Personal Hygiene', 'Medication Management', 'Companionship'],
                'safety_concerns_notes': 'Prone to wandering in the evening.',
                'schedule_type': 'Daily',
                'care_continuity': 'Long-term',
                'schedule_details': 'M-F 9am-5pm, plus occasional Sat morning.',
                'gender_preference': 'Female',
                'preferred_temperament': 'Calm and Patient',
                'communication_style': 'Soft-spoken and detailed',
                'social_preference': 'Engaged conversation (hobbies, history)',
                'care_attitude': 'Gentle but firm when necessary',
                'routine_tolerance': 'High adherence to routine required',
                'home_accessibility': 'Wheelchair ramp, accessible bathroom',
                'smoking_policy': 'Non-smoking home',
                'environment_factors': ['Has a friendly cat', 'Quiet neighborhood'],
                'favorite_topics': 'Gardening, Classic movies, Local history',
                'topics_to_avoid': 'Politics, Financial discussions',
                'cultural_religious_needs': ['Weekly church attendance (Sunday)'],
                'cultural_religious_detail_notes': 'Respect for Christian traditions.'
            }
        
        # Fallback for other patients
        return dict(client_data)

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
                    SELECT c.* FROM caretakers c
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

    def create_match(self, patient_id: int, caregiver_id: int, match_score: float, compatibility_factors: dict):
        """Save a match result to the database."""
        with _database_connect() as conn:
            with conn.cursor() as cur:
                # Convert the complex dict into a JSON string for storage
                factors_json = json.dumps(compatibility_factors)
                
                cur.execute("""
                    -- FIX: Renamed 'caregiver_id' column to 'caretaker_id'
                    INSERT INTO matches (patient_id, caretaker_id, match_score, compatibility_factors)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                """, (patient_id, caregiver_id, match_score, factors_json))
                return cur.fetchone()[0]

    def delete_matches_by_patient(self, patient_id: int):
        """Deletes all existing match records for a given patient."""
        with _database_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM matches 
                    WHERE patient_id = %s;
                """, (patient_id,))