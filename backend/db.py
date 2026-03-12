"""
Database initialization module
Sets up SQLite database tables for:
- System commands (applications)
- Web commands (websites)
- Contacts (phone numbers)
"""

import sqlite3
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database file path
DB_PATH = "jarvis.db"


def init_database():
    """
    Initialize the database with required tables
    Creates tables if they don't exist
    """
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
        logger.info("sys_command table created/verified")
        
        # Table for web commands (websites)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS web_command (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                url VARCHAR(1000) NOT NULL
            )
        """)
        logger.info("web_command table created/verified")
        
        # Table for contacts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) UNIQUE NOT NULL,
                phone VARCHAR(255) NOT NULL,
                email VARCHAR(255)
            )
        """)
        logger.info("contacts table created/verified")
        
        conn.commit()
        logger.info("Database initialization complete")
        
        return conn, cursor
        
    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}", exc_info=True)
        raise


def add_system_command(name: str, path: str) -> bool:
    """
    Add a system command to the database
    
    Args:
        name: Application name
        path: Full path to executable
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO sys_command (name, path) VALUES (?, ?)",
            (name.lower(), path)
        )
        conn.commit()
        logger.info(f"Added system command: {name}")
        return True
        
    except sqlite3.IntegrityError:
        logger.warning(f"System command '{name}' already exists")
        return False
    except Exception as e:
        logger.error(f"Error adding system command: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()


def add_web_command(name: str, url: str) -> bool:
    """
    Add a web command to the database
    
    Args:
        name: Website name
        url: Website URL
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO web_command (name, url) VALUES (?, ?)",
            (name.lower(), url)
        )
        conn.commit()
        logger.info(f"Added web command: {name}")
        return True
        
    except sqlite3.IntegrityError:
        logger.warning(f"Web command '{name}' already exists")
        return False
    except Exception as e:
        logger.error(f"Error adding web command: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()


def add_contact(name: str, phone: str, email: str = None) -> bool:
    """
    Add a contact to the database
    
    Args:
        name: Contact name
        phone: Phone number
        email: Email address (optional)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)",
            (name, phone, email)
        )
        conn.commit()
        logger.info(f"Added contact: {name}")
        return True
        
    except sqlite3.IntegrityError:
        logger.warning(f"Contact '{name}' already exists")
        return False
    except Exception as e:
        logger.error(f"Error adding contact: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()


def get_system_command(name: str) -> str:
    """
    Get the path for a system command
    
    Args:
        name: Application name
        
    Returns:
        Path to executable or None
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT path FROM sys_command WHERE LOWER(name) = ?",
            (name.lower(),)
        )
        result = cursor.fetchone()
        return result[0] if result else None
        
    except Exception as e:
        logger.error(f"Error retrieving system command: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()


def get_web_command(name: str) -> str:
    """
    Get the URL for a web command
    
    Args:
        name: Website name
        
    Returns:
        Website URL or None
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT url FROM web_command WHERE LOWER(name) = ?",
            (name.lower(),)
        )
        result = cursor.fetchone()
        return result[0] if result else None
        
    except Exception as e:
        logger.error(f"Error retrieving web command: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()


def get_contact_phone(name: str) -> str:
    """
    Get phone number for a contact
    
    Args:
        name: Contact name
        
    Returns:
        Phone number or None
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT phone FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) = ?",
            (f'%{name.lower()}%', name.lower())
        )
        result = cursor.fetchone()
        return result[0] if result else None
        
    except Exception as e:
        logger.error(f"Error retrieving contact: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()


# Initialize database on module import
if __name__ == "__main__":
    try:
        init_database()
        logger.info("Database ready for use")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")