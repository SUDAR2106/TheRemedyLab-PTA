# init_db.py
from db import create_tables

if __name__ == "__main__":
    create_tables()
    print("SQLite database and tables created successfully!")