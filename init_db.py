#!/usr/bin/env python3
"""
Database initialization and setup script
Run this once to initialize the database with sample data
"""

import sqlite3
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DB_PATH = "jarvis.db"

def init_database():
    """Initialize the database with required tables"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Table for system commands (applications)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sys_command (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                path VARCHAR(1000) NOT NULL
            )
        """)
        
        # Table for web commands (websites)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS web_command (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                url VARCHAR(1000) NOT NULL
            )
        """)
        
        # Table for contacts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) UNIQUE NOT NULL,
                phone VARCHAR(255) NOT NULL,
                email VARCHAR(255)
            )
        """)
        
        conn.commit()
        logger.info("Database tables created/verified")
        
        return conn, cursor
        
    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
        raise


def add_sample_data(conn, cursor):
    """Add sample system commands, web commands, and contacts"""
    
    # Sample system commands
    sample_commands = [
        ("notepad", "C:\\Windows\\System32\\notepad.exe"),
        ("calculator", "C:\\Windows\\System32\\calc.exe"),
        ("cmd", "C:\\Windows\\System32\\cmd.exe"),
        ("paint", "C:\\Windows\\System32\\mspaint.exe"),
    ]
    
    # Sample web commands
    sample_web = [
        ("google", "https://www.google.com"),
        ("youtube", "https://www.youtube.com"),
        ("gmail", "https://mail.google.com"),
        ("github", "https://www.github.com"),
        ("stack overflow", "https://stackoverflow.com"),
    ]
    
    # Sample contacts
    sample_contacts = [
        ("alice", "9876543210", "alice@example.com"),
        ("bob", "9123456780", "bob@example.com"),
        ("charlie", "8987654321", "charlie@example.com"),
    ]
    
    try:
        for name, path in sample_commands:
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO sys_command (name, path) VALUES (?, ?)",
                    (name.lower(), path)
                )
                logger.info(f"Added system command: {name}")
            except sqlite3.IntegrityError:
                logger.info(f"System command '{name}' already exists")
        
        for name, url in sample_web:
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO web_command (name, url) VALUES (?, ?)",
                    (name.lower(), url)
                )
                logger.info(f"Added web command: {name}")
            except sqlite3.IntegrityError:
                logger.info(f"Web command '{name}' already exists")
        
        for name, phone, email in sample_contacts:
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO contacts (name, phone, email) VALUES (?, ?, ?)",
                    (name.lower(), phone, email)
                )
                logger.info(f"Added contact: {name}")
            except sqlite3.IntegrityError:
                logger.info(f"Contact '{name}' already exists")
        
        conn.commit()
        logger.info("Sample data added successfully")
        
    except Exception as e:
        logger.error(f"Error adding sample data: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        logger.info("Initializing database...")
        conn, cursor = init_database()
        
        logger.info("Adding sample data...")
        add_sample_data(conn, cursor)
        
        logger.info("Database initialization complete!")
        print("\n✅ Database initialized successfully!")
        print("\nYou can now:")
        print("1. Add your own system commands to the database")
        print("2. Add your own web commands to the database")
        print("3. Add your own contacts to the database")
        print("\nTo run Jarvis, execute: python run.py")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
