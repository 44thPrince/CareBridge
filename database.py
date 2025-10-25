import psycopg2
from psycopg2.extras import DictCursor
from contextlib import contextmanager

@contextmanager
def _database_connect():
    connection = psycopg2.connect(dbname='apt_manager')
    try:
        with connection:
            yield connection
    finally:
        connection.close()

class DatabasePersistence:
    def find_user_by_username(self, username):
        with _database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE username = %s", (username,))
                return cur.fetchone()

    def all_apartments(self):
        with _database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT a.id AS apartment_id, a.unit_number, a.building_name, a.rent,
                        t.id AS tenant_id, t.name AS tenant_name
                    FROM apartments a
                    LEFT JOIN tenants t ON a.id = t.apartment_id
                    ORDER BY a.building_name, a.unit_number, t.name
                """)
                rows = cursor.fetchall()

        apartments = {}
        for row in rows:
            apt_id = row["apartment_id"]
            if apt_id not in apartments:
                apartments[apt_id] = {
                    "id": apt_id,
                    "unit_number": row["unit_number"],
                    "building_name": row["building_name"],
                    "rent": row["rent"],
                    "tenants": []
                }
            if row["tenant_id"]:
                apartments[apt_id]["tenants"].append({
                    "id": row["tenant_id"],
                    "name": row["tenant_name"]
                })

        return list(apartments.values())
            
    def create_apartment(self, unit_number, building_name, rent):
        with _database_connect() as connection:
            with connection.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    INSERT INTO apartments (unit_number, building_name, rent)
                    VALUES (%s, %s, %s)
                """, (unit_number, building_name, rent))

    def find_apartment(self, apt_id):
        with _database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT a.id, a.unit_number, a.building_name, a.rent,
                           t.name AS tenant_name
                    FROM apartments a
                    LEFT JOIN tenants t ON a.id = t.apartment_id
                    WHERE a.id = %s
                """, (apt_id,))
                return cur.fetchone()
    
    def update_apartment(self, apt_id, unit_number, building_name, rent):
        with _database_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE apartments
                    SET unit_number = %s,
                        building_name = %s,
                        rent = %s
                    WHERE id = %s
                """, (unit_number, building_name, rent, apt_id))

    def find_apartment_by_unit_and_building(self, unit_number, building_name):
        """Validation helper to ensure we dont throw integrity error
            due to our unique contraint on our apartments table"""
        with _database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT * FROM apartments
                    WHERE unit_number = %s AND building_name = %s
                """, (unit_number, building_name))
                return cur.fetchone()
            
    def delete_apartment(self, apt_id):
        with _database_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM apartments WHERE id = %s", (apt_id,))

    def all_tenants(self):
        with _database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT t.id, t.name, a.unit_number, a.building_name
                    FROM tenants t
                    JOIN apartments a ON t.apartment_id = a.id
                    ORDER BY a.building_name, a.unit_number, t.name
                """)
                return cur.fetchall()

    def create_tenant(self, name, apartment_id):
        with _database_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO tenants (name, apartment_id)
                    VALUES (%s, %s)
                """, (name, apartment_id))

    def find_tenant(self, tenant_id):
        with _database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT t.id, t.name, t.apartment_id,
                        a.unit_number, a.building_name
                    FROM tenants t
                    JOIN apartments a ON t.apartment_id = a.id
                    WHERE t.id = %s
                """, (tenant_id,))
                return cur.fetchone()

    def update_tenant(self, tenant_id, name):
        with _database_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE tenants
                    SET name = %s
                    WHERE id = %s
                """, (name, tenant_id))

    def delete_tenant(self, tenant_id):
        with _database_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tenants WHERE id = %s", (tenant_id,))
