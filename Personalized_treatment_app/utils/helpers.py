# utils/helpers.py

import datetime

def format_date_for_display(iso_date_string):
    """
    Formats an ISO date string (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS.ffffff)
    into a more readable 'DD Mon YYYY' format.
    Handles potential variations in ISO string precision.
    """
    if not iso_date_string:
        return "N/A"
    
    try:
        # Try parsing with microsecond precision first
        dt_object = datetime.datetime.fromisoformat(iso_date_string)
    except ValueError:
        try:
            # Fallback to parsing without microseconds
            dt_object = datetime.datetime.strptime(iso_date_string.split('.')[0], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            # Fallback to parsing just a date
            dt_object = datetime.datetime.strptime(iso_date_string.split('T')[0], "%Y-%m-%d")
            
    return dt_object.strftime("%d %b %Y") # e.g., "01 Jan 2023"

def calculate_age(dob_iso_string):
    """
    Calculates age in years from an ISO date string of birth.
    Returns None if the date string is invalid or missing.
    """
    if not dob_iso_string:
        return None
    try:
        # Assuming YYYY-MM-DD format for DOB from database
        dob = datetime.datetime.strptime(dob_iso_string, "%Y-%m-%d").date()
        today = datetime.date.today()
        # Calculate age
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    except ValueError:
        return None # Invalid date format


# You can add more general helper functions here as your project grows.
# For example:
# def validate_email_format(email):
#     """Basic email format validation."""
#     import re
#     return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

# def sanitize_filename(filename):
#     """Removes potentially problematic characters from a filename."""
#     import re
#     return re.sub(r'[^\w\-. ]', '', filename)