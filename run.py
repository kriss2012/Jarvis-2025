"""
Entry point for Jarvis-2025 application
Manages two separate processes: Main UI and Hotword Detection
"""

import multiprocessing
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def startJarvis():
    """
    Start the main Jarvis application with Eel UI
    Runs in Process 1
    """
    try:
        logger.info("Process 1 Starting: Main Jarvis Application")
        from main import start
        start()
    except Exception as e:
        logger.error(f"Error in startJarvis: {str(e)}", exc_info=True)
        sys.exit(1)


def listenHotword():
    """
    Listen for hotword activation (Jarvis, Alexa)
    Runs in Process 2
    """
    try:
        logger.info("Process 2 Starting: Hotword Listener")
        from backend.feature import hotword
        hotword()
    except Exception as e:
        logger.error(f"Error in listenHotword: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        # Set multiprocessing start method (important for Windows)
        if sys.platform == "win32":
            multiprocessing.set_start_method("spawn", force=True)
        
        # Create processes
        process1 = multiprocessing.Process(target=startJarvis, name="JarvisMain")
        process2 = multiprocessing.Process(target=listenHotword, name="HotwordListener")
        
        # Start both processes
        logger.info("Starting Jarvis-2025...")
        process1.start()
        process2.start()
        
        # Wait for main process to complete
        process1.join()
        
        # Clean up hotword listener
        if process2.is_alive():
            logger.info("Terminating hotword listener process...")
            process2.terminate()
            process2.join(timeout=5)
            if process2.is_alive():
                process2.kill()
                process2.join()
        
        logger.info("System terminated successfully.")
        
    except Exception as e:
        logger.error(f"Critical error in main: {str(e)}", exc_info=True)
        sys.exit(1)