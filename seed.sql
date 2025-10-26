-- ========================================
-- CareBridge Database Schema for pgAdmin4
-- ========================================
-- 
-- INSTRUCTIONS FOR pgAdmin4:
-- 1. First, run the DROP/CREATE DATABASE commands below in the postgres database
-- 2. Then, right-click on the new 'carebridgedb' database and select "Query Tool"
-- 3. Copy and paste the rest of this file (starting from "-- Tables") into that query tool
-- 4. Execute to create all tables and seed data
-- ========================================

-- STEP 1: Run this section while connected to the 'postgres' database
-- ========================================
DROP DATABASE IF EXISTS carebridgedb;
CREATE DATABASE carebridgedb;

-- ========================================
-- STEP 2: Now connect to 'carebridgedb' and run everything below
-- ========================================

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
  address TEXT,
  emergency_contact_name TEXT,
  emergency_contact_phone TEXT,
  medical_conditions TEXT,
  special_instructions TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE caretakers (
  id SERIAL PRIMARY KEY,
  full_name TEXT NOT NULL,
  phone_number TEXT UNIQUE NOT NULL,
  email TEXT,
  date_of_birth DATE NOT NULL,
  address TEXT,
  city TEXT,
  state TEXT,
  zip_code TEXT,
  bio TEXT,
  years_experience INT DEFAULT 0,
  hourly_rate DECIMAL(10,2),
  availability TEXT, -- e.g., "Monday-Friday, 9am-5pm"
  certifications TEXT, -- comma-separated list
  languages TEXT, -- comma-separated list
  background_check_status TEXT DEFAULT 'pending',
  profile_image_url TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ADL (Activities of Daily Living) Services Table
CREATE TABLE caretaker_adls (
  id SERIAL PRIMARY KEY,
  caretaker_id INT NOT NULL REFERENCES caretakers(id) ON DELETE CASCADE,
  service_type TEXT NOT NULL,
  is_available BOOLEAN DEFAULT TRUE,
  notes TEXT,
  CONSTRAINT unique_caretaker_service UNIQUE (caretaker_id, service_type)
);

-- ADL Service Types Enum
-- This will track what services each caretaker provides
CREATE TABLE adl_service_types (
  id SERIAL PRIMARY KEY,
  category TEXT NOT NULL, -- 'basic_adl', 'instrumental_adl', 'specialized_care'
  service_name TEXT NOT NULL UNIQUE,
  description TEXT,
  display_order INT
);

-- Demo users with bcrypt hashed passwords
-- password is "secret123" for admin
-- password is "demo123" for demo users
INSERT INTO users (username, password_hash)
VALUES 
  ('admin', '$2b$12$mFqYPtWtKidDOVNuKVuMC.gx6Bw470JfwG/yz0fPMy5pfBJO0qnL6'),
  ('client1', '$2b$12$6.ZOuKjZyEziTg8J35o8KejHgMNLlFiVEn2gA1ZM3d5rD9Vj8divG'),
  ('caretaker1', '$2b$12$6.ZOuKjZyEziTg8J35o8KejHgMNLlFiVEn2gA1ZM3d5rD9Vj8divG');

-- Seed ADL Service Types
INSERT INTO adl_service_types (category, service_name, description, display_order) VALUES
-- Basic ADLs
('basic_adl', 'Bathing & Personal Hygiene', 'Assistance with bathing, showering, and personal hygiene', 1),
('basic_adl', 'Dressing Assistance', 'Help with dressing and undressing', 2),
('basic_adl', 'Eating & Feeding', 'Meal assistance and feeding support', 3),
('basic_adl', 'Mobility & Transfers', 'Help with walking, transferring from bed to chair', 4),
('basic_adl', 'Toileting Assistance', 'Help with toileting and continence care', 5),
-- Instrumental ADLs
('instrumental_adl', 'Meal Planning & Preparation', 'Planning and cooking nutritious meals', 6),
('instrumental_adl', 'Housekeeping', 'Cleaning, organizing, and maintaining home', 7),
('instrumental_adl', 'Laundry', 'Washing, drying, and folding clothes', 8),
('instrumental_adl', 'Transportation', 'Driving to appointments, errands, social activities', 9),
('instrumental_adl', 'Shopping & Errands', 'Grocery shopping and running errands', 10),
('instrumental_adl', 'Medication Management', 'Reminding and assisting with medications', 11),
('instrumental_adl', 'Technology Assistance', 'Help with phones, tablets, computers', 12),
-- Specialized Care
('specialized_care', 'Dementia & Alzheimer Care', 'Specialized care for memory conditions', 13),
('specialized_care', 'Physical Therapy Assistance', 'Support with prescribed exercises', 14),
('specialized_care', 'Medical Equipment Management', 'Help with medical devices and equipment', 15),
('specialized_care', 'Emergency Response', '24/7 emergency response and monitoring', 16),
('specialized_care', 'Companionship', 'Social interaction, conversation, emotional support', 17);

-- Seed: clients
INSERT INTO clients (full_name, phone_number, date_of_birth, address, emergency_contact_name, emergency_contact_phone, medical_conditions, special_instructions)
VALUES
('Alice Johnson', '555-1111', '1945-08-12', '123 Main St', 'Bob Johnson', '555-1112', NULL, NULL),
('Mark Davis', '555-2222', '1960-03-05', '456 Elm St', 'Mary Davis', '555-2223', NULL, NULL),
('Demo Client', 'client1', '1950-01-01', '123 Demo Street, Orlando, FL', 'Jane Smith', '555-0101', 'Mild arthritis, needs assistance with mobility', 'Prefers morning appointments, likes classical music');

-- Seed: caretakers with ADL capabilities
INSERT INTO caretakers (full_name, phone_number, email, date_of_birth, address, city, state, zip_code, bio, years_experience, hourly_rate, availability, certifications, languages, background_check_status)
VALUES
('Sarah Lee', '555-3333', 'sarah.lee@carebridge.com', '1985-05-15', '789 Oak Ave', 'Orlando', 'FL', '32801', 
 'Compassionate caregiver with 8 years of experience helping seniors maintain independence. Specialized in dementia care and medication management.',
 8, 25.00, 'Monday-Friday, 9am-5pm', 'CPR, Certified Nursing Assistant', 'English, Spanish', 'verified'),
('David Kim', '555-4444', 'david.kim@carebridge.com', '1988-09-22', '321 Pine St', 'Orlando', 'FL', '32804',
 'Experienced caregiver specializing in mobility assistance and physical therapy support. Passionate about improving quality of life.',
 5, 22.00, 'Flexible availability', 'CPR, Physical Therapy Aide', 'English, Korean', 'verified'),
('Maria Rodriguez', '555-5555', 'maria.rodriguez@carebridge.com', '1990-03-10', '654 Maple Dr', 'Orlando', 'FL', '32803',
 'Dedicated caregiver with a heart for serving veterans and seniors. Bilingual in English and Spanish with background in meal planning.',
 4, 20.00, 'Monday-Saturday, 8am-6pm', 'First Aid, Food Safety', 'English, Spanish', 'verified');

-- Seed: Caretaker ADL Services
-- Sarah Lee's services
INSERT INTO caretaker_adls (caretaker_id, service_type, is_available, notes) VALUES
(1, 'Bathing & Personal Hygiene', TRUE, 'Specialize in dementia patients'),
(1, 'Medication Management', TRUE, NULL),
(1, 'Meal Planning & Preparation', TRUE, 'Nutrition-conscious meals'),
(1, 'Dementia & Alzheimer Care', TRUE, '5 years specialized experience'),
(1, 'Companionship', TRUE, 'Excellent at social engagement');

-- David Kim's services
INSERT INTO caretaker_adls (caretaker_id, service_type, is_available, notes) VALUES
(2, 'Mobility & Transfers', TRUE, 'Strong background in PT assistance'),
(2, 'Physical Therapy Assistance', TRUE, NULL),
(2, 'Transportation', TRUE, 'Clean driving record'),
(2, 'Medical Equipment Management', TRUE, 'Trained on various devices'),
(2, 'Housekeeping', TRUE, NULL);

-- Maria Rodriguez's services
INSERT INTO caretaker_adls (caretaker_id, service_type, is_available, notes) VALUES
(3, 'Meal Planning & Preparation', TRUE, 'Certified in food safety'),
(3, 'Shopping & Errands', TRUE, NULL),
(3, 'Laundry', TRUE, NULL),
(3, 'Companionship', TRUE, 'Bilingual, great with communication'),
(3, 'Housekeeping', TRUE, 'Thorough and detail-oriented');