import os

# Directory configurations
UPLOAD_DIR = "uploads"
DOWNLOAD_DIR = "downloads"
STRUCTURED_DIR = "structured_dataset"
RECORDS_FILENAME = "records.csv"

# Derived paths
RECORDS_PATH = os.path.join(STRUCTURED_DIR, RECORDS_FILENAME)

# Ensure all directories exist
for folder in [UPLOAD_DIR, DOWNLOAD_DIR, STRUCTURED_DIR]:
    os.makedirs(folder, exist_ok=True)
