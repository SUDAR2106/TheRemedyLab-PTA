# services/userid_generator_service.py

import sqlite3

def generate_custom_user_id(user_type: str, db_path: str = "healthcare.db") -> str:
    """
    Generate a user ID like P0001 or D0001 based on user type.

    Args:
        user_type (str): 'patient' or 'doctor'
        db_path (str): Path to the SQLite database

    Returns:
        str: Custom user ID
    """
    prefix = "P" if user_type == "patient" else "D"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT user_id FROM users
        WHERE user_id LIKE ?
        ORDER BY user_id DESC
        LIMIT 1;
    """, (f"{prefix}%",))

    result = cursor.fetchone()
    conn.close()

    if result:
        last_id_num = int(result[0][1:])  # remove 'P' or 'D' and parse the number
        new_id = f"{prefix}{last_id_num + 1:04d}"
    else:
        new_id = f"{prefix}0001"

    return new_id