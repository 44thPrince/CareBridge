--create db
DROP DATABASE IF EXISTS carebridgedb;
CREATE DATABASE carebridgedb;

\c apt_manager

-- Tables
CREATE TABLE users (
    id serial PRIMARY KEY,
    username text UNIQUE NOT NULL,
    password_hash text NOT NULL
);

CREATE TABLE clients (
  id SERIAL PRIMARY KEY,
  full_name TEXT NOT NULL,
  phone_number TEXT UNIQUE NOT NULL,
  date_of_birth DATE NOT NULL,
  address TEXT
);

CREATE TABLE caretakers (
  id SERIAL PRIMARY KEY,
  full_name TEXT NOT NULL,
  phone_number TEXT UNIQUE NOT NULL,
  date_of_birth DATE NOT NULL
);

-- password is "secret123"
INSERT INTO users (username, password_hash)
VALUES (
  'admin',
  '$2b$12$mFqYPtWtKidDOVNuKVuMC.gx6Bw470JfwG/yz0fPMy5pfBJO0qnL6'
);

-- Seed: clients
INSERT INTO clients (full_name, phone_number, date_of_birth, address)
VALUES
('Alice Johnson', '555-1111', '1945-08-12', '123 Main St'),
('Mark Davis', '555-2222', '1960-03-05', '456 Elm St');

-- Seed: caretaker
INSERT INTO caretakers (full_name, phone_number)
VALUES
('Sarah Lee', '555-3333'),
('David Kim', '555-4444');
