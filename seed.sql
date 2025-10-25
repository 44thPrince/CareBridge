--create db
DROP DATABASE IF EXISTS apt_manager;
CREATE DATABASE apt_manager;

\c apt_manager

-- Tables
CREATE TABLE users (
    id serial PRIMARY KEY,
    username text UNIQUE NOT NULL,
    password_hash text NOT NULL
);

CREATE TABLE apartments (
    id serial PRIMARY KEY,
    unit_number text NOT NULL,
    building_name text NOT NULL,
    rent numeric(8,2) NOT NULL,
    UNIQUE (unit_number, building_name)
);

CREATE TABLE tenants (
    id serial PRIMARY KEY,
    name text NOT NULL,
    apartment_id integer NOT NULL
        REFERENCES apartments(id) ON DELETE CASCADE
);

-- password is "secret123"
INSERT INTO users (username, password_hash)
VALUES (
  'admin',
  '$2b$12$mFqYPtWtKidDOVNuKVuMC.gx6Bw470JfwG/yz0fPMy5pfBJO0qnL6'
);

-- Seed: apartments
INSERT INTO apartments (unit_number, building_name, rent)
VALUES
  ('101', 'Maple', 1200.00),
  ('102', 'Maple', 950.00),
  ('201', 'Oak', 1500.00),
  ('101', 'Arturo', 1399.99),
  ('102', 'Arturo', 1400.00),
  ('102', 'Modu5', 1400.00);


-- Seed: tenants
INSERT INTO tenants (name, apartment_id)
VALUES
  ('John Doe', 1),
  ('Jane Smith', 2),
  ('Eric Young', 1),
  ('Sean O''Malley', 3),
  ('Merab Divalishi', 5),
  ('Cocoa Cat', 4);

