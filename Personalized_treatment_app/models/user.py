#models/user.py

import uuid
import datetime
# Import the security utility functions
from utils import security # Assuming utils/security.py is in a 'utils' directory relative to where your models are run
from database.db_utils import DBManager



class User:
    def __init__(self, user_id: str, username: str, password_hash: str, user_type: str, 
                 first_name: str = None, last_name: str = None, email: str = None, 
                 created_at: str = None, updated_at: str = None):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.user_type = user_type 
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.created_at = created_at if created_at else datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.updated_at = updated_at 

    @classmethod
    def create(cls, username: str, password: str, user_type: str, 
               first_name: str = None, last_name: str = None, email: str = None) -> 'User':
        """
        Creates a new user, hashes the password using security utility, and saves them to the database.
        Returns a User object if successful, None otherwise.
        """
        from services.userid_generator_service import generate_custom_user_id
        user_id = generate_custom_user_id(user_type)
        hashed_password = security.hash_password(password) # Using the utility function
        created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        updated_at = created_at 
        
        query = """
            INSERT INTO users (user_id, username, password_hash, user_type, first_name, last_name, email, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        success = DBManager.execute_query(
            query,
            (user_id, username, hashed_password, user_type, first_name, last_name, email, created_at, updated_at)
        )
        if success:
            print(f"User '{username}' created successfully.")
            return cls(user_id, username, hashed_password, user_type, first_name, last_name, email, created_at, updated_at)
        return None

    @classmethod
    def get_by_username(cls, username: str) -> 'User':
        """Finds a user by their username."""
        query = "SELECT * FROM users WHERE username = ?"
        user_data = DBManager.fetch_one(query, (username,))
        if user_data:
            return cls(**user_data)
        return None

    @classmethod
    def get_by_user_id(cls, user_id: str) -> 'User':
        """Finds a user by their user_id."""
        query = "SELECT * FROM users WHERE user_id = ?"
        user_data = DBManager.fetch_one(query, (user_id,))
        if user_data:
            return cls(**user_data)
        return None
    
    @classmethod
    def get_by_email(cls, email: str) -> 'User':
        """Finds a user by their email address."""
        query = "SELECT * FROM users WHERE email = ?"
        user_data = DBManager.fetch_one(query, (email,))
        if user_data:
            return cls(**user_data)
        return None

    def verify_password(self, password: str) -> bool:
        """Verifies a given password against the stored hashed password using security utility."""
        return security.check_password(password, self.password_hash) # Using the utility function

    def update_profile(self, first_name: str = None, last_name: str = None, email: str = None) -> bool:
        """
        Updates user profile details (first_name, last_name, email)
        and sets the updated_at timestamp.
        """
        self.first_name = first_name if first_name is not None else self.first_name
        self.last_name = last_name if last_name is not None else self.last_name
        self.email = email if email is not None else self.email
        self.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        query = """
            UPDATE users SET first_name = ?, last_name = ?, email = ?, updated_at = ?
            WHERE user_id = ?
        """
        success = DBManager.execute_query(
            query,
            (self.first_name, self.last_name, self.email, self.updated_at, self.user_id)
        )
        if success:
            print(f"User '{self.username}' profile updated.")
        return success

    def delete(self) -> bool:
        """Deletes a user from the database."""
        query = "DELETE FROM users WHERE user_id = ?"
        return DBManager.execute_query(query, (self.user_id,))

    def to_dict(self):
        """Converts user object to a dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "user_type": self.user_type, 
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }