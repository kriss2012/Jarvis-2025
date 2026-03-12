#!/usr/bin/env python3
"""
Jarvis-2025 All-in-One Initialization Script
Run this to set up everything needed for Jarvis
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directories():
    """Create required directories"""
    directories = [
        "logs",
        "backups",
        "backend/auth/trainer",
        "frontend/assets/audio",
        "frontend/assets/img",
        "frontend/assets/vendore",
    ]
    
    print("\n📁 Creating directories...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {directory}")


def create_database():
    """Create and populate the database"""
    print("\n📊 Initializing database...")
    
    db_path = "jarvis.db"
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
    
    print("  ✅ Tables created")
    
    # Add sample data
    system_apps = [
        ("notepad", "C:\\Windows\\System32\\notepad.exe"),
        ("calculator", "C:\\Windows\\System32\\calc.exe"),
        ("cmd", "C:\\Windows\\System32\\cmd.exe"),
        ("paint", "C:\\Windows\\System32\\mspaint.exe"),
        ("explorer", "C:\\Windows\\explorer.exe"),
    ]
    
    web_apps = [
        ("google", "https://www.google.com"),
        ("youtube", "https://www.youtube.com"),
        ("gmail", "https://mail.google.com"),
        ("github", "https://www.github.com"),
        ("stackoverflow", "https://stackoverflow.com"),
    ]
    
    sample_contacts = [
        ("alice", "9876543210", "alice@example.com"),
        ("bob", "9123456780", "bob@example.com"),
        ("charlie", "8987654321", "charlie@example.com"),
    ]
    
    # Insert sample data
    for name, path in system_apps:
        try:
            cursor.execute(
                "INSERT INTO sys_command (name, path) VALUES (?, ?)",
                (name.lower(), path)
            )
        except sqlite3.IntegrityError:
            pass
    
    for name, url in web_apps:
        try:
            cursor.execute(
                "INSERT INTO web_command (name, url) VALUES (?, ?)",
                (name.lower(), url)
            )
        except sqlite3.IntegrityError:
            pass
    
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
    print("  ✅ Sample data added")


def create_cookie_file():
    """Create cookie template"""
    print("\n🔑 Creating HuggingFace cookie template...")
    
    cookie_path = os.path.join("backend", "cookie.json")
    
    if not os.path.exists(cookie_path):
        try:
            with open(cookie_path, 'w') as f:
                f.write("[]")
            print(f"  ✅ Created: {cookie_path}")
            print("     TODO: Add your HuggingFace cookies here")
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
    else:
        print(f"  ✅ Already exists: {cookie_path}")


def check_packages():
    """Check if required packages are installed"""
    print("\n📦 Checking required packages...")
    
    packages = {
        'cv2': 'OpenCV',
        'eel': 'Eel',
        'pygame': 'Pygame',
        'pyaudio': 'PyAudio',
        'pyttsx3': 'pyttsx3',
        'speech_recognition': 'SpeechRecognition',
        'pywhatkit': 'PyWhatKit',
        'pvporcupine': 'Porcupine',
        'hugchat': 'HuggingChat',
        'numpy': 'NumPy',
    }
    
    missing = []
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name}")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Run all initialization steps"""
    print("\n" + "="*60)
    print("JARVIS-2025 INITIALIZATION".center(60))
    print("="*60)
    
    try:
        create_directories()
        create_database()
        create_cookie_file()
        
        all_packages = check_packages()
        
        print("\n" + "="*60)
        if all_packages:
            print("✅ INITIALIZATION COMPLETE!".center(60))
        else:
            print("⚠️  INITIALIZATION PARTIAL".center(60))
        print("="*60)
        
        print("\n📝 Next Steps:")
        print("  1. Install missing packages (if any)")
        print("  2. Add HuggingFace cookies to: backend/cookie.json")
        print("  3. Run: python run.py")
        
        print("\n📚 Documentation:")
        print("  - See README.md for detailed instructions")
        print("  - Run: python diagnostic.py for diagnostics")
        
        print()
        
    except Exception as e:
        logger.error(f"Initialization failed: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
