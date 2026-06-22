# User Authentication logic (registration, password hashing, validation)
import hashlib
from test_codebase import database
from test_codebase.models import User

def hash_password(password: str) -> str:
    """
    Computes a secure SHA-256 hash of a plain text password
    using Python's built-in hashlib library.
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user(username: str, password: str) -> bool:
    """
    Registers a new user by hashing their password and storing
    their record inside the sqlite database.
    Returns True if registration succeeds, False if username exists.
    """
    password_hash = hash_password(password)
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()
        success = True
    except Exception:
        # Handles UNIQUE constraint failure for duplicate usernames
        success = False
    finally:
        conn.close()
        
    return success

def verify_login(username: str, password: str) -> User | None:
    """
    Verifies user login credentials. Compares hash of incoming
    password against the stored db hash.
    Returns a User model object if valid, otherwise returns None.
    """
    password_hash = hash_password(password)
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ? AND password_hash = ?",
        (username, password_hash)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return User(user_id=row['id'], username=row['username'], password_hash=row['password_hash'])
    return None
