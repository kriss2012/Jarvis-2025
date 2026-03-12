"""
Command handling module for voice commands and text-to-speech
Manages all voice interactions with the assistant
"""

import time
import pyttsx3
import speech_recognition as sr
import eel
import logging
from typing import Optional
import os

# Import intelligent modules
from backend.intelligent_processor import CommandProcessor
from backend.jarvis_personality import JarvisPersonality
from backend.language_manager import LanguageManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize intelligent modules
command_processor = CommandProcessor()
jarvis = JarvisPersonality(name="Jarvis")
language_manager = LanguageManager()


def speak(text: str) -> None:
    """
    Convert text to speech and display on UI
    
    Args:
        text: The text to speak
    """
    try:
        text = str(text)
        logger.info(f"Speaking: {text}")
        
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        
        # Pick a voice safely with fallback
        voice_to_use = None
        if len(voices) > 2:
            voice_to_use = voices[2].id  # Preferred voice
        elif len(voices) > 0:
            voice_to_use = voices[0].id  # Fallback voice
        
        if voice_to_use:
            engine.setProperty('voice', voice_to_use)
        
        engine.setProperty('rate', 174)  # Speech rate
        
        # Update UI
        try:
            eel.DisplayMessage(text)
        except Exception as e:
            logger.warning(f"Could not update DisplayMessage: {str(e)}")
        
        # Speak the text
        engine.say(text)
        engine.runAndWait()
        
        try:
            eel.receiverText(text)
        except Exception as e:
            logger.warning(f"Could not update receiverText: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error in speak: {str(e)}", exc_info=True)


def takecommand() -> Optional[str]:
    """
    Listen for voice input from microphone and convert to text
    Supports multiple languages (English, Hindi, Marathi)
    
    Returns:
        The recognized text in lowercase, or None if recognition failed
    """
    try:
        r = sr.Recognizer()
        current_language = language_manager.current_language
        language_code = language_manager.get_language_code(current_language)
        
        with sr.Microphone() as source:
            lang_name = language_manager.get_current_language_name()
            logger.info(f"Listening for command in {lang_name}...")
            
            try:
                eel.DisplayMessage(f"Listening in {lang_name}...")
            except Exception as e:
                logger.warning(f"Could not update UI: {str(e)}")
            
            r.pause_threshold = 1
            r.adjust_for_ambient_noise(source, duration=1)
            
            # Listen for audio (timeout=10s, phrase_time_limit=8s)
            audio = r.listen(source, timeout=10, phrase_time_limit=8)
            
            try:
                logger.info("Recognizing...")
                eel.DisplayMessage("Recognizing...")
            except Exception as e:
                logger.warning(f"Could not update UI: {str(e)}")
            
            # Recognize speech using Google Speech Recognition with language support
            query = r.recognize_google(audio, language=language_code)
            logger.info(f"User said ({lang_name}): {query}")
            
            try:
                eel.DisplayMessage(query)
            except Exception as e:
                logger.warning(f"Could not update UI: {str(e)}")
            
            # Speak back confirmation
            speak(query)
            return query.lower()
            
    except sr.UnknownValueError:
        logger.warning("Could not understand audio")
        error_msg = get_localized_message("could_not_understand", language_manager.current_language)
        try:
            eel.DisplayMessage(error_msg)
        except Exception as e:
            logger.warning(f"Could not update UI: {str(e)}")
        speak(error_msg)
        return None
    except sr.RequestError as e:
        logger.error(f"Speech Recognition error: {str(e)}")
        error_msg = f"Speech recognition error: {str(e)}"
        speak(error_msg)
        return None
    except Exception as e:
        logger.error(f"Error in takecommand: {str(e)}", exc_info=True)
        return None


def get_localized_message(message_key: str, language: str = 'en') -> str:
    """Get localized messages"""
    messages = {
        'could_not_understand': {
            'en': "Sorry, I could not understand what you said",
            'hi': "माफ़ी चाहता हूं, मैं समझ नहीं पाया आपने क्या कहा",
            'mr': "माफ करा, मी समजू शकलो नाही तुम्ही काय म्हणालात"
        },
        'language_changed': {
            'en': "Language changed to English",
            'hi': "भाषा हिंदी में बदल दी गई है",
            'mr': "भाषा मराठी मध्ये बदली गेली आहे"
        },
        'send_message': {
            'en': "What message to send?",
            'hi': "क्या संदेश भेजना है?",
            'mr': "काय संदेश पाठवायचा?"
        },
        'cookies_missing': {
            'en': "HuggingFace cookies not configured. Please add cookies for AI chat.",
            'hi': "HuggingFace कुकीज़ कॉन्फ़िगर नहीं हैं। कृपया कुकीज़ जोड़ें।",
            'mr': "HuggingFace कुकीज कॉन्फिगर नहीं आहेत। कृपया कुकीज जोडा।"
        },
        'cookies_empty': {
            'en': "HuggingFace cookies are not configured. Add your cookies to backend/cookie.json to enable AI chat.",
            'hi': "HuggingFace कुकीज़ कॉन्फ़िगर नहीं हैं। backend/cookie.json में कुकीज़ जोड़ें।",
            'mr': "HuggingFace कुकीज कॉन्फिगर नहीं आहेत। backend/cookie.json मध्ये कुकीज जोडा।"
        },
        'try_specific_command': {
            'en': "Unable to process your request. Please try a specific command like 'open notepad' or 'play on YouTube'.",
            'hi': "आपके अनुरोध को प्रोसेस नहीं कर सका। कृपया कोई विशिष्ट आदेश दें जैसे 'नोटपैड खोलो'।",
            'mr': "तुमच्या विनंतीवर प्रक्रिया करू शकलो नाही। कृपया विशिष्ट आदेश द्या जसे 'नोटपॅड उघडा'।"
        }
    }
    return messages.get(message_key, {}).get(language, messages.get(message_key, {}).get('en', ""))


@eel.expose
def takeAllCommands(message: Optional[str] = None) -> None:
    """
    Main command handler - processes both voice and text input
    Exposed to JavaScript/Frontend
    
    Args:
        message: Optional text message from UI (overrides voice input)
    """
    try:
        if message is None:
            # Listen for voice input
            query = takecommand()
            
            if not query:
                logger.warning("No command received")
                return
            
            logger.info(f"Query from voice: {query}")
        else:
            # Use provided message
            query = message.lower()
            logger.info(f"Query from message: {query}")
        
        # Send query to UI
        try:
            eel.senderText(query)
        except Exception as e:
            logger.warning(f"Could not send text to UI: {str(e)}")
        
        # Process the command
        processCommand(query)
        
    except Exception as e:
        logger.error(f"Error in takeAllCommands: {str(e)}", exc_info=True)
        speak("Sorry, something went wrong.")
        try:
            eel.ShowHood()
        except Exception as eel_error:
            logger.warning(f"Could not show UI: {str(eel_error)}")


def processCommand(query: str) -> None:
    """
    Process the voice command with intelligent understanding
    Uses fuzzy matching and context awareness
    
    Args:
        query: The user's command text
    """
    try:
        if not query:
            speak("No command was given.")
            return
        
        logger.info(f"Processing command: {query}")
        current_language = language_manager.current_language
        
        # Understand command intent
        intent = command_processor.understand_intent(query, current_language)
        logger.info(f"Intent identified: {intent}")
        
        # Get Jarvis response
        if intent['type']:
            response = jarvis.get_confirmation(current_language)
            speak(response)
        
        command_type = intent['type']
        entity = intent['entity']
        
        # Handle language switching
        if command_type == 'language':
            handle_language_change(query)
            return
        
        # Command: Open application
        if command_type == 'open_app' or "open" in query:
            from backend.feature import openCommand
            openCommand(query)
        
        # Command: WhatsApp messaging/calling
        elif command_type == 'whatsapp' or "send message" in query or "call" in query or "video call" in query:
            from backend.feature import findContact, whatsApp
            
            phone, name = findContact(query)
            
            if phone != 0:
                if "send message" in query:
                    flag = 'message'
                    msg_prompt = get_localized_message("send_message", current_language)
                    speak(msg_prompt)
                    msg_query = takecommand()
                elif "call" in query:
                    flag = 'call'
                    msg_query = ""
                else:
                    flag = 'video call'
                    msg_query = ""
                
                whatsApp(phone, msg_query if msg_query else "", flag, name)
        
        # Command: Play YouTube video
        elif command_type == 'youtube' or "on youtube" in query or "youtube" in query:
            from backend.feature import PlayYoutube
            PlayYoutube(query)
        
        # Command: Get current time
        elif command_type == 'time':
            handle_time_command(current_language)
        
        # Command: Get current date
        elif command_type == 'date':
            handle_date_command(current_language)
        
        # Command: Chat with AI (with fallback if cookies missing)
        else:
            try:
                cookie_path = os.path.join("backend", "cookie.json")
                
                if not os.path.exists(cookie_path):
                    msg = get_localized_message("cookies_missing", current_language)
                    speak(msg)
                    return
                
                # Check if cookies file has valid content
                with open(cookie_path, 'r') as f:
                    content = f.read().strip()
                    if content == "[]" or not content:
                        msg = get_localized_message("cookies_empty", current_language)
                        speak(msg)
                        return
                
                from backend.feature import chatBot
                chatBot(query)
            except FileNotFoundError:
                speak("HuggingFace cookies file not found.")
            except Exception as e:
                logger.warning(f"Chat error: {str(e)}")
                help_msg = get_localized_message("try_specific_command", current_language)
                speak(help_msg)
        
        # Update interaction count
        jarvis.increment_interactions()
        
    except Exception as e:
        logger.error(f"Error processing command: {str(e)}", exc_info=True)
        error_response = jarvis.get_apology(language_manager.current_language)
        speak(error_response)
    finally:
        # Show UI after command completes
        try:
            eel.ShowHood()
        except Exception as e:
            logger.warning(f"Could not show UI: {str(e)}")


def handle_language_change(query: str):
    """Handle language switching command"""
    current_language = language_manager.current_language
    
    if 'hindi' in query.lower() or 'हिंदी' in query:
        language_manager.set_language('hi')
        speak("भाषा हिंदी में बदल दी गई है")
    elif 'marathi' in query.lower() or 'मराठी' in query:
        language_manager.set_language('mr')
        speak("भाषा मराठी मध्ये बदली गेली आहे")
    elif 'english' in query.lower() or 'अंग्रेजी' in query:
        language_manager.set_language('en')
        speak("Language changed to English")
    else:
        # Show available languages
        if current_language == 'en':
            speak("Available languages: English, Hindi, Marathi. Please specify which language.")
        elif current_language == 'hi':
            speak("उपलब्ध भाषाएं: अंग्रेजी, हिंदी, मराठी। कृपया भाषा निर्दिष्ट करें।")
        else:
            speak("उपलब्ध भाषा: इंग्लिश, हिंदी, मराठी। कृपया भाषा निर्दिष्ट करा।")


def handle_time_command(language: str = 'en'):
    """Handle time request"""
    from datetime import datetime
    current_time = datetime.now().strftime("%I:%M %p")
    
    time_messages = {
        'en': f"The current time is {current_time}, sir.",
        'hi': f"वर्तमान समय {current_time} है।",
        'mr': f"वर्तमान वेळ {current_time} आहे।"
    }
    
    speak(time_messages.get(language, time_messages['en']))


def handle_date_command(language: str = 'en'):
    """Handle date request"""
    from datetime import datetime
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    
    date_messages = {
        'en': f"Today's date is {current_date}, sir.",
        'hi': f"आज की तारीख {current_date} है।",
        'mr': f"आजची तारीख {current_date} आहे।"
    }
    
    speak(date_messages.get(language, date_messages['en']))