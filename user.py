from dataclasses import dataclass
from typing import Optional
import hashlib
from flask import session
from database import Database

@dataclass
class User:
    id: str
    email: str
    username: str
    password_hash: str

    @classmethod
    def create(cls, email: str, username: str, password: str) -> Optional['User']:
        # Check if the email or username is already taken
        existing_user = cls.get_user_by_email(email) or cls.get_user_by_username(username)
        if existing_user:
            return None

        # Hash the password
        password_hash = cls.hash_password(password)

        # Create a new user
        new_id = cls.get_next_user_id()
        return cls(new_id, email, username, password_hash)

    @classmethod
    def authenticate(cls, identifier: str, password: str) -> Optional['User']:
        # Fetch the user by email or username
        user = cls.get_user_by_email(identifier) or cls.get_user_by_username(identifier)
        if not user:
            print(f"User not found for identifier: {identifier}")
            return None

        # Check if the password is correct
        if cls.verify_password(password, user.password_hash):
            print(f"Authentication successful for user: {user.username}")
            return user
        else:
            print(f"Authentication failed for user: {user.username}")
            return None

    @classmethod
    def get_current_user(cls) -> Optional['User']:
        # Retrieve the current user from the session
        user_id = session.get('user_id')
        if user_id:
            return cls.get_user_by_id(user_id)
        else:
            return None

    @classmethod
    def get_user_by_id(cls, user_id: str) -> Optional['User']:
        database = Database()
        user_data = database.get_user_by_id(user_id)
        if user_data:
            return cls(user_id, user_data['email'], user_data['username'], user_data['password_hash'])
        else:
            return None

    @classmethod
    def get_user_by_email(cls, email: str) -> Optional['User']:
        database = Database()
        for user_id, user_data in database.data['users'].items():
            if user_data['email'] == email:
                return cls(user_id, user_data['email'], user_data['username'], user_data['password_hash'])
        return None

    @classmethod
    def get_user_by_username(cls, username: str) -> Optional['User']:
        database = Database()
        for user_id, user_data in database.data['users'].items():
            if user_data['username'] == username:
                return cls(user_id, user_data['email'], user_data['username'], user_data['password_hash'])
        return None

    @classmethod
    def get_next_user_id(cls) -> str:
        database = Database()
        if not database.data['users']:
            return '1'
        try:
            user_ids = [int(user_id) for user_id in database.data['users'] if user_id.isdigit()]
            return str(max(user_ids, default=0) + 1)
        except ValueError:
            # If there's an issue with the existing IDs, start from 1
            return '1'

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return hashlib.sha256(password.encode()).hexdigest() == hashed_password