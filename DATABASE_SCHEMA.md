# CareBridge Database Schema

## Overview
This document describes the database schema for CareBridge, a platform connecting caregivers with clients (elderly, disabled, veterans, and people with chronic conditions).

## Schema Diagram

```
users
  ├── id (PK)
  ├── username (UNIQUE)
  └── password_hash

clients
  ├── id (PK)
  ├── full_name
  ├── phone_number (UNIQUE)
  ├── date_of_birth
  ├── address
  ├── emergency_contact_name
  ├── emergency_contact_phone
  ├── medical_conditions
  ├── special_instructions
  └── created_at

caretakers
  ├── id (PK)
  ├── full_name
  ├── phone_number (UNIQUE)
  ├── email
  ├── date_of_birth
  ├── address
  ├── city
  ├── state
  ├── zip_code
  ├── bio
  ├── years_experience
  ├── hourly_rate
  ├── availability
  ├── certifications
  ├── languages
  ├── background_check_status
  ├── profile_image_url
  └── created_at

adl_service_types
  ├── id (PK)
  ├── category (basic_adl, instrumental_adl, specialized_care)
  ├── service_name (UNIQUE)
  ├── description
  └── display_order

caretaker_adls (Junction Table)
  ├── id (PK)
  ├── caretaker_id (FK → caretakers)
  ├── service_type
  ├── is_available
  ├── notes
  └── UNIQUE (caretaker_id, service_type)
```

## Table Details

### `users`
Authentication table for platform users.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique identifier |
| username | TEXT UNIQUE NOT NULL | Login username |
| password_hash | TEXT NOT NULL | Hashed password |

### `clients`
Clients who need care services.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique identifier |
| full_name | TEXT NOT NULL | Client's full name |
| phone_number | TEXT UNIQUE NOT NULL | Contact phone |
| date_of_birth | DATE NOT NULL | Birth date |
| address | TEXT | Physical address |
| emergency_contact_name | TEXT | Emergency contact |
| emergency_contact_phone | TEXT | Emergency contact phone |
| medical_conditions | TEXT | Medical history |
| special_instructions | TEXT | Special care instructions |
| created_at | TIMESTAMP | Account creation date |

### `caretakers`
Caretakers providing services.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique identifier |
| full_name | TEXT NOT NULL | Caretaker's name |
| phone_number | TEXT UNIQUE NOT NULL | Contact phone |
| email | TEXT | Email address |
| date_of_birth | DATE NOT NULL | Birth date |
| address | TEXT | Physical address |
| city | TEXT | City |
| state | TEXT | State |
| zip_code | TEXT | ZIP code |
| bio | TEXT | Personal bio |
| years_experience | INT DEFAULT 0 | Years of experience |
| hourly_rate | DECIMAL(10,2) | Hourly rate |
| availability | TEXT | Available hours |
| certifications | TEXT | Comma-separated certifications |
| languages | TEXT | Comma-separated languages |
| background_check_status | TEXT DEFAULT 'pending' | Background check status |
| profile_image_url | TEXT | Profile image URL |
| created_at | TIMESTAMP | Account creation date |

### `adl_service_types`
Standard ADL service types.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique identifier |
| category | TEXT NOT NULL | Service category |
| service_name | TEXT UNIQUE NOT NULL | Service name |
| description | TEXT | Service description |
| display_order | INT | Display order |

**Categories:**
- `basic_adl`: Basic Activities of Daily Living
- `instrumental_adl`: Instrumental Activities of Daily Living
- `specialized_care`: Specialized care services

### `caretaker_adls`
Junction table mapping caretakers to their ADL capabilities.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique identifier |
| caretaker_id | INT NOT NULL | FK to caretakers |
| service_type | TEXT NOT NULL | Service type name |
| is_available | BOOLEAN DEFAULT TRUE | Service availability |
| notes | TEXT | Additional notes |

## ADL Service Types

### Basic ADLs
1. Bathing & Personal Hygiene
2. Dressing Assistance
3. Eating & Feeding
4. Mobility & Transfers
5. Toileting Assistance

### Instrumental ADLs
6. Meal Planning & Preparation
7. Housekeeping
8. Laundry
9. Transportation
10. Shopping & Errands
11. Medication Management
12. Technology Assistance

### Specialized Care
13. Dementia & Alzheimer Care
14. Physical Therapy Assistance
15. Medical Equipment Management
16. Emergency Response
17. Companionship

## Database Methods

### Client Methods
- `insert_client()` - Create new client
- `find_user_by_username()` - Find user by username

### Caretaker Methods
- `insert_caretaker()` - Create new caretaker
- `get_all_caretakers()` - List all caretakers
- `get_caretaker_by_id()` - Get specific caretaker

### ADL Methods
- `get_all_adl_services()` - List all ADL services
- `get_adls_by_category()` - Filter by category
- `get_caretaker_adls()` - Get caretaker's services
- `search_caretakers_by_adl()` - Find caretakers by service
- `add_caretaker_adl()` - Add service to caretaker
- `remove_caretaker_adl()` - Remove service from caretaker

## Indexes

Primary keys are automatically indexed. Consider adding indexes on:
- `caretakers.background_check_status`
- `caretaker_adls.caretaker_id`
- `caretaker_adls.service_type`
- `caretaker_adls.is_available`

## Data Integrity

1. **Unique Constraints**: Phone numbers are unique for both clients and caretakers
2. **Foreign Keys**: Cascading deletes for caretaker_adls when caretakers are deleted
3. **Service Types**: Standardized service names prevent duplicates
4. **Background Checks**: Required for caretaker verification

