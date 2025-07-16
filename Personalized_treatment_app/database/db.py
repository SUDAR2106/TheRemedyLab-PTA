# database/db.py
import sqlite3
import os
from config import DATABASE_FILE # Ensure DATABASE_FILE is defined in your config.py

# Global variables to hold the single database connection and cursor
_conn = None
_cursor = None

def init_db():
    """
    Initializes the global database connection and creates tables if they don't exist.
    This function should be called once, typically at the very start of the application.
    """
    global _conn, _cursor
    if _conn is None:
        # Ensure the directory for the database file exists
        db_dir = os.path.dirname(DATABASE_FILE)
        if db_dir: # Check if db_dir is not empty (e.g., if DATABASE_FILE is just a filename)
            os.makedirs(db_dir, exist_ok=True)

        # Connect to the SQLite database.
        # check_same_thread=False is crucial for Streamlit as it can access DB from different threads.
        _conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
        _conn.row_factory = sqlite3.Row # Allows accessing columns by name (e.g., row['column_name'])
        _conn.execute("PRAGMA foreign_keys = ON;") # Ensure foreign keys are enforced

        _cursor = _conn.cursor()
        _create_tables()
        print(f"Database connection established successfully at: {DATABASE_FILE}")
    else:
        print("Database connection already established.")

def _create_tables():
    """Private helper to create all necessary database tables."""
    global _cursor, _conn

    # Users table - EXACTLY as per your new requirement
    _cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            user_type TEXT NOT NULL, -- e.g., 'patient', 'doctor', 'admin'
            first_name TEXT,
            last_name TEXT,
            email TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    print("Table 'users' checked/created.")

    # Patients table
    _cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            user_id TEXT UNIQUE NOT NULL,
            date_of_birth TEXT, -- ISO format date string (YYYY-MM-DD)
            gender TEXT,
            contact_number TEXT,
            address TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        );
    ''')
    print("Table 'patients' checked/created.")

    # Doctors table
    _cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id TEXT PRIMARY KEY,
            user_id TEXT UNIQUE NOT NULL,
            medical_license_number TEXT UNIQUE, -- Unique for each doctor
            specialization TEXT,
            contact_number TEXT,
            hospital_affiliation TEXT,
            is_available INTEGER DEFAULT 1, -- New: 1 for available, 0 for not available
            last_assignment_date TEXT,     -- New: To help with workload balancing
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        );
    ''')
    print("Table 'doctors' checked/created.")

    # Health Reports table
    _cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_reports (
            report_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            uploaded_by TEXT NOT NULL, -- user_id of who uploaded (can be patient or doctor)
            report_type TEXT NOT NULL,
            file_type TEXT NOT NULL, -- e.g., 'pdf','docx','csv','json','image', etc.
            upload_date TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            extracted_data_json TEXT, -- JSON string of data extracted by parser
            assigned_doctor_id TEXT, -- New: Doctor assigned to this specific report       
            processing_status TEXT NOT NULL, -- e.g., 'pending_extraction', 'extracted', 'processing_ai', 'ready_for_review'
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id) ON DELETE CASCADE,
            FOREIGN KEY (uploaded_by) REFERENCES users (user_id) ON DELETE CASCADE
        );
    ''')
    print("Table 'health_reports' checked/created.")

    # Recommendations table
    _cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            recommendation_id TEXT PRIMARY KEY,
            report_id TEXT NOT NULL,
            patient_id TEXT NOT NULL,
            ai_generated_treatment TEXT,
            ai_generated_lifestyle TEXT,
            ai_generated_priority TEXT,
            doctor_id TEXT, -- NULL until reviewed
            doctor_notes TEXT,
            status TEXT NOT NULL, -- e.g., 'AI_generated', 'approved_by_doctor', 'modified_by_doctor', 'rejected_by_doctor'
            reviewed_date TEXT,
            approved_treatment TEXT,
            approved_lifestyle TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (report_id) REFERENCES health_reports (report_id) ON DELETE CASCADE,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id) ON DELETE CASCADE,
            FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id) ON DELETE SET NULL
        );
    ''')
    print("Table 'recommendations' checked/created.")

    # Patient-Doctor Mapping table
    _cursor.execute('''
        CREATE TABLE IF NOT EXISTS patient_doctor_mapping (
            mapping_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            doctor_id TEXT NOT NULL,
            assigned_date TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1, -- 1 for active, 0 for inactive
            -- Removed UNIQUE(patient_id, doctor_id) to allow multiple assignments over time, if needed
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id) ON DELETE CASCADE,
            FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id) ON DELETE CASCADE
        );
    ''')
    print("Table 'patient_doctor_mapping' checked/created.")

    # New table for Report Type to Specialist Mapping
    _cursor.execute('''
        CREATE TABLE IF NOT EXISTS report_specialist_mapping (
            report_type TEXT PRIMARY KEY,
            specialization_required TEXT NOT NULL
        );
    ''')
    print("Table 'report_specialist_mapping' checked/created.")

    _conn.commit()
    print("All necessary tables checked/created.")

def get_db_connection():
    """Returns the current persistent database connection object."""
    global _conn
    if _conn is None:
        raise RuntimeError("Database connection not initialized. Call init_db() first.")
    return _conn

def get_db_cursor():
    """Returns the current persistent database cursor object."""
    global _cursor
    if _cursor is None:
        raise RuntimeError("Database cursor not initialized. Call init_db() first.")
    return _cursor

def close_db_connection():
    """Closes the database connection. Call this when the application exits."""
    global _conn, _cursor
    if _conn:
        _conn.close()
        _conn = None
        _cursor = None
        print("Database connection closed.")