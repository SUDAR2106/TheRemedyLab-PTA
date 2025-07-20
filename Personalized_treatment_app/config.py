# config.py

import os
import logging

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLite database file path
DATABASE_FILE = os.path.join(BASE_DIR, 'healthcare.db')

# Upload directory for health reports
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')

# Create the upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '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')

# Log directory
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Default log file
LOG_FILE = os.path.join(LOG_DIR, 'application.log')

# ------------------------
# Logging Configuration
# ------------------------

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

# Shortcut logger for each module
logger = logging.getLogger("remedylab")