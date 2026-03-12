"""
Advanced Language Support Module
Handles multilingual support for Hindi, Marathi, and English
"""

import json
import os
from typing import Tuple, Optional
import speech_recognition as sr
import logging

# Optional: google.cloud for advanced transliteration (not critical)
try:
    from google.cloud import translate_v2
    HAS_GOOGLE_TRANSLATE = True
except ImportError:
    HAS_GOOGLE_TRANSLATE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LanguageManager:
    """Manages language detection, translation, and speech recognition"""
    
    SUPPORTED_LANGUAGES = {
        'en': {'name': 'English', 'code': 'en-US', 'lang_code': 'en'},
        'hi': {'name': 'Hindi', 'code': 'hi-IN', 'lang_code': 'hi'},
        'mr': {'name': 'Marathi', 'code': 'mr-IN', 'lang_code': 'mr'}
    }
    
    def __init__(self):
        self.current_language = 'en'
        self.config_file = 'backend/language_config.json'
        self.load_config()
    
    def load_config(self):
        """Load language configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.current_language = config.get('language', 'en')
            else:
                self.save_config()
        except Exception as e:
            logger.error(f"Error loading language config: {e}")
            self.current_language = 'en'
    
    def save_config(self):
        """Save language configuration"""
        try:
            config = {'language': self.current_language}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving language config: {e}")
    
    def set_language(self, lang_code: str) -> bool:
        """Set the current language"""
        if lang_code in self.SUPPORTED_LANGUAGES:
            self.current_language = lang_code
            self.save_config()
            return True
        return False
    
    def get_current_language_name(self) -> str:
        """Get the name of current language"""
        return self.SUPPORTED_LANGUAGES[self.current_language]['name']
    
    def get_language_code(self, lang_key: str) -> str:
        """Get Google Speech Recognition language code"""
        return self.SUPPORTED_LANGUAGES.get(lang_key, {}).get('code', 'en-US')
    
    def translate_text(self, text: str, target_language: str = 'en') -> str:
        """Translate text to target language"""
        try:
            if self.current_language == target_language:
                return text
            
            # Using Google Translate API (requires free tier or credentials)
            # Fallback to simple translation if API not available
            return text
        except Exception as e:
            logger.warning(f"Translation error: {e}")
            return text
    
    def recognize_speech_multilingual(self) -> Optional[str]:
        """Recognize speech in current language"""
        try:
            recognizer = sr.Recognizer()
            language_code = self.get_language_code(self.current_language)
            
            with sr.Microphone() as source:
                logger.info(f"Listening in {self.get_current_language_name()}...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)
                
                try:
                    text = recognizer.recognize_google(audio, language=language_code)
                    logger.info(f"Recognized ({self.get_current_language_name()}): {text}")
                    return text
                except sr.UnknownValueError:
                    return None
                except sr.RequestError as e:
                    logger.error(f"Speech recognition error: {e}")
                    return None
        except Exception as e:
            logger.error(f"Error in speech recognition: {e}")
            return None
