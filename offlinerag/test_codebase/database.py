# Database engine initialization and session mock
import sqlite3
from test_codebase import config

def get_db_connection():
    """
    Creates and returns a connection to the SQLite database
    configured in our config.py file.
    """
    connection = sqlite3.connect(config.DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_database():
    """
    Prepares database tables by running initial CREATE queries.
    Saves a clean schema setup for users and posts.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create the Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Create the Posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database tables initialized successfully.")
