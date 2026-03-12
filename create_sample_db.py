#!/usr/bin/env python3
"""
Create sample database for Jarvis-2025
This initializes the database with example data
"""

import sqlite3
import os
from pathlib import Path

def create_sample_db():
    """Create and populate the sample database"""
    db_path = "jarvis.db"
    
    # Check if database already exists
    db_exists = os.path.exists(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sys_command (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) UNIQUE NOT NULL,
            path VARCHAR(1000) NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS web_command (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) UNIQUE NOT NULL,
            url VARCHAR(1000) NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) UNIQUE NOT NULL,
            phone VARCHAR(255) NOT NULL,
            email VARCHAR(255)
        )
    """)
    
    if not db_exists:
        # Add sample system commands (Windows)
        system_apps = [
            ("notepad", "C:\\Windows\\System32\\notepad.exe"),
            ("calculator", "C:\\Windows\\System32\\calc.exe"),
            ("cmd", "C:\\Windows\\System32\\cmd.exe"),
            ("paint", "C:\\Windows\\System32\\mspaint.exe"),
            ("explorer", "C:\\Windows\\explorer.exe"),
        ]
        
        for name, path in system_apps:
            try:
                cursor.execute(
                    "INSERT INTO sys_command (name, path) VALUES (?, ?)",
                    (name.lower(), path)
                )
            except sqlite3.IntegrityError:
                pass
        
        # Add sample web commands
        web_apps = [
            ("google", "https://www.google.com"),
            ("youtube", "https://www.youtube.com"),
            ("gmail", "https://mail.google.com"),
            ("github", "https://www.github.com"),
            ("stackoverflow", "https://stackoverflow.com"),
            ("twitter", "https://www.twitter.com"),
            ("facebook", "https://www.facebook.com"),
            ("whatsapp", "https://web.whatsapp.com"),
        ]
        
        for name, url in web_apps:
            try:
                cursor.execute(
                    "INSERT INTO web_command (name, url) VALUES (?, ?)",
                    (name.lower(), url)
                )
            except sqlite3.IntegrityError:
                pass
        
        # Add sample contacts
        sample_contacts = [
            ("alice", "9876543210", "alice@example.com"),
            ("bob", "9123456780", "bob@example.com"),
            ("charlie", "8987654321", "charlie@example.com"),
        ]
        
        for name, phone, email in sample_contacts:
            try:
                cursor.execute(
                    "INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)",
                    (name.lower(), phone, email)
                )
            except sqlite3.IntegrityError:
                pass
    
    conn.commit()
    conn.close()
    
    print("✅ Database initialized successfully!")


if __name__ == "__main__":
    create_sample_db()
