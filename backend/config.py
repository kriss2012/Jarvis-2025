"""
Configuration module
Contains all configuration settings for Jarvis-2025
"""

# Assistant name
ASSISTANT_NAME = "jarvis"

# Speech rate (words per minute)
SPEECH_RATE = 174

# API Keys and Tokens
HUGGINGFACE_TOKEN = "YOUR_HUGGINGFACE_TOKEN"  # Set your token here

# Database configuration
DATABASE_PATH = "jarvis.db"
DATABASE_BACKUP_PATH = "backups/jarvis_backup.db"

# Face Recognition settings
FACE_RECOGNITION_CONFIDENCE_THRESHOLD = 45  # Lower is more confident
FACE_CAPTURE_IMAGE_COUNT = 30

# Audio settings
MICROPHONE_TIMEOUT_SECONDS = 10
MICROPHONE_PHRASE_LIMIT_SECONDS = 8
MICROPHONE_PAUSE_THRESHOLD = 1

# UI Settings
UI_HOST = "localhost"
UI_PORT = 8000
UI_MODE = "edge"  # 'edge', 'chrome', or None

# Path settings
FRONTEND_PATH = "frontend"
BACKEND_PATH = "backend"
AUDIO_ASSETS_PATH = "frontend/assets/audio"
SOUND_FILE = "start_sound.mp3"

# Feature flags
ENABLE_HOTWORD_DETECTION = True
ENABLE_FACE_RECOGNITION = True
ENABLE_VOICE_INPUT = True
ENABLE_TEXT_INPUT = True
ENABLE_YOUTUBE = True
ENABLE_WHATSAPP = True
ENABLE_AI_CHAT = True
ENABLE_SYSTEM_COMMANDS = True
ENABLE_WEB_COMMANDS = True

# Hotword settings
HOTWORD_KEYWORDS = ["jarvis", "alexa"]
HOTWORD_SENSITIVITY = 0.5

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = "logs/jarvis.log"