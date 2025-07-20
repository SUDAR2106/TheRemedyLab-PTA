# config.py

import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLite database file path
DATABASE_FILE = os.path.join(BASE_DIR, 'healthcare.db')

# Upload directory for health reports
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')

# Create the upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')