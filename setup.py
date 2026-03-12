#!/usr/bin/env python3
"""
Setup script for Jarvis-2025
Initializes all required directories, files, and database
Run this before running the application for the first time
"""

import os
import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directories():
    """Create required directories if they don't exist"""
    directories = [
        "logs",
        "backups",
        "backend/auth/trainer",
        "frontend/assets/audio",
        "frontend/assets/img",
        "frontend/assets/vendore",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Directory created/verified: {directory}")
    
    print("\n✅ All directories created/verified")


def create_cookie_template():
    """Create a template cookie.json file"""
    cookie_path = os.path.join("backend", "cookie.json")
    
    if not os.path.exists(cookie_path):
        # Create an empty template
        template = "[]"
        try:
            with open(cookie_path, 'w') as f:
                f.write(template)
            logger.info(f"✅ Created cookie template: {cookie_path}")
            print(f"\n⚠️  Template created: {cookie_path}")
            print("   Please add your HuggingFace cookies (export from browser as JSON)")
        except Exception as e:
            logger.error(f"Error creating cookie template: {str(e)}")
    else:
        logger.info(f"✅ Cookie file already exists: {cookie_path}")


def init_database():
    """Initialize the database"""
    try:
        # Import the init_db module
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from init_db import init_database, add_sample_data
        
        logger.info("Initializing database...")
        conn, cursor = init_database()
        add_sample_data(conn, cursor)
        conn.close()
        
        logger.info("✅ Database initialized successfully")
        print("\n✅ Database initialized with sample data")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        print(f"\n⚠️  Database initialization issue: {str(e)}")


def verify_requirements():
    """Check if all required packages are installed"""
    required_packages = {
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
    for module, name in required_packages.items():
        try:
            __import__(module)
            logger.info(f"✅ {name} is installed")
        except ImportError:
            logger.warning(f"❌ {name} is NOT installed")
            missing.append(name)
    
    if missing:
        print("\n⚠️  Missing packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nRun: pip install -r requirements.txt")
        return False
    
    print("\n✅ All required packages are installed")
    return True


def main():
    """Run all setup steps"""
    print("\n" + "="*60)
    print("JARVIS-2025 SETUP".center(60))
    print("="*60 + "\n")
    
    try:
        # Step 1: Create directories
        print("Step 1: Creating directories...")
        create_directories()
        
        # Step 2: Verify requirements
        print("\nStep 2: Checking requirements...")
        if not verify_requirements():
            print("\n⚠️  Please install missing packages first")
            print("   Run: pip install -r requirements.txt")
            return False
        
        # Step 3: Initialize database
        print("\nStep 3: Initializing database...")
        init_database()
        
        # Step 4: Create cookie template
        print("\nStep 4: Setting up HuggingFace integration...")
        create_cookie_template()
        
        # Success
        print("\n" + "="*60)
        print("SETUP COMPLETED SUCCESSFULLY!".center(60))
        print("="*60)
        print("\nNext steps:")
        print("1. Add your HuggingFace cookies to: backend/cookie.json")
        print("2. Train face recognition (optional): python backend/auth/trainer.py")
        print("3. Run Jarvis: python run.py")
        print("\nFor help, see README.md")
        print()
        
        return True
        
    except Exception as e:
        logger.error(f"Setup failed: {str(e)}", exc_info=True)
        print(f"\n❌ Setup failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
