# database/db_utils.py
import sqlite3
# Import all necessary functions/globals from your db.py
from database.db import init_db, get_db_connection, get_db_cursor, close_db_connection

class DBManager:
    # No need for init_db or _ensure_db_initialized here.
    # init_db() is called directly from main_app.py

    @classmethod
    def execute_query(cls, query: str, params=()):
        """Executes a SQL query with optional parameters."""
        try:
            conn = get_db_connection()
            cursor = get_db_cursor()
            cursor.execute(query, params)
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error executing query: {query} with params {params}. Error: {e}")
            return False

    @classmethod
    def fetch_one(cls, query: str, params=()):
        """Fetches a single row from the database, returned as a dictionary (due to row_factory)."""
        try:
            cursor = get_db_cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"Database error fetching one row: {query} with params {params}. Error: {e}")
            return None

    @classmethod
    def fetch_all(cls, query: str, params=()):
        """Fetches all rows from the database, returned as a list of dictionaries."""
        try:
            cursor = get_db_cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            if rows:
                return [dict(row) for row in rows]
            return []
        except sqlite3.Error as e:
            print(f"Database error fetching all rows: {query} with params {params}. Error: {e}")
            return []
    
    @classmethod
    def close_connection(cls):
        """Closes the database connection."""
        close_db_connection()