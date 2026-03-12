"""
Main application file - Initializes Eel UI and handles authentication
"""

import os
import sys
import logging
import eel
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from backend.auth.recoganize import AuthenticateFace
    from backend.feature import play_assistant_sound
    from backend.command import speak
except ImportError as e:
    logger.error(f"Import error: {str(e)}")
    sys.exit(1)


def start():
    """
    Initialize Eel and start the web interface
    """
    try:
        # Initialize Eel with frontend directory
        frontend_path = Path("frontend").absolute()
        if not frontend_path.exists():
            logger.error(f"Frontend directory not found: {frontend_path}")
            sys.exit(1)
        
        eel.init("frontend")
        play_assistant_sound()
        
        @eel.expose
        def init():
            """
            Initialize the application after UI loads
            Handles face authentication
            """
            try:
                eel.hideLoader()
                speak("Welcome to Jarvis")
                speak("Ready for Face Authentication")
                
                # Attempt face recognition
                flag = AuthenticateFace()
                
                if flag == 1:
                    # Face recognized successfully
                    speak("Face recognized successfully")
                    eel.hideFaceAuth()
                    eel.hideFaceAuthSuccess()
                    speak("Welcome to Your Assistant")
                    eel.hideStart()
                    play_assistant_sound()
                    return True
                else:
                    # Face not recognized
                    speak("Face not recognized. Please try again")
                    # Try again or exit
                    return False
                    
            except Exception as e:
                logger.error(f"Error in init: {str(e)}", exc_info=True)
                speak("An error occurred during authentication")
                return False
        
        # Start Eel with proper error handling
        logger.info("Starting Eel server...")
        eel.start(
            "index.html",
            mode="edge",  # Changed from None to 'edge' for better compatibility
            host="localhost",
            port=8000,
            block=True
        )
        
    except Exception as e:
        logger.error(f"Error in start: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    start()