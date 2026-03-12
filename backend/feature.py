# import playsound
# import eel
# @eel.expose
# def playAssistantSound():
#     music_dir = "frontend\\assets\\audio\\start_sound.mp3"
#     playsound(music_dir)

import os
import re
from shlex import quote
import struct
import subprocess
import time
import webbrowser
import eel
from hugchat import hugchat
import pvporcupine
import pyaudio
import pyautogui
import pywhatkit as kit
import pygame
from backend.command import speak
from backend.config import ASSISTANT_NAME
import sqlite3
from backend.helper import extract_yt_term, remove_words

conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()

# Initialize pygame mixer
pygame.mixer.init()

# Define the function to play sound
@eel.expose
def play_assistant_sound():
    """Play the assistant activation sound"""
    try:
        # Use a project-relative path so the audio file works across machines
        sound_file = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                   'frontend', 'assets', 'audio', 'start_sound.mp3'))
        if os.path.exists(sound_file):
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()
        else:
            print(f"play_assistant_sound: file not found: {sound_file}")
    except Exception as e:
        print(f"Error playing sound: {e}")

def openCommand(query):
    """Open applications or websites based on query"""
    try:
        query = query.replace(ASSISTANT_NAME, "")
        query = query.replace("open", "")
        query = query.lower()
        app_name = query.strip()

        if app_name != "":
            try:
                cursor.execute(
                    'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                if len(results) != 0:
                    speak("Opening " + query)
                    os.startfile(results[0][0])
                elif len(results) == 0:
                    cursor.execute(
                        'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                    results = cursor.fetchall()
                    if len(results) != 0:
                        speak("Opening " + query)
                        webbrowser.open(results[0][0])
                    else:
                        speak("Opening " + query)
                        try:
                            os.system('start ' + query)
                        except Exception as e:
                            print(f"Error opening app: {e}")
                            speak("not found")
            except Exception as e:
                print(f"Error in openCommand query: {e}")
                speak("some thing went wrong")
    except Exception as e:
        print(f"openCommand error: {e}")
        speak("Error opening application")

def PlayYoutube(query):
    """Search and play YouTube video"""
    try:
        search_term = extract_yt_term(query)
        speak("Playing " + search_term + " on YouTube")
        kit.playonyt(search_term)
    except Exception as e:
        print(f"PlayYoutube error: {e}")
        speak("Error playing YouTube video")

def hotword():
    """Listen for hotword (Jarvis/Alexa) detection"""
    porcupine = None
    paud = None
    audio_stream = None
    
    try:
        # pre trained keywords
        porcupine = pvporcupine.create(keywords=["jarvis", "alexa"])
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        print("Hotword listener started...")
        # loop for streaming
        while True:
            try:
                keyword = audio_stream.read(porcupine.frame_length)
                keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)

                # processing keyword comes from mic
                keyword_index = porcupine.process(keyword)

                # checking if keyword detected
                if keyword_index >= 0:
                    print("hotword detected")
                    # pressing shortcut key win+j
                    import pyautogui as autogui
                    autogui.keyDown("win")
                    autogui.press("j")
                    time.sleep(2)
                    autogui.keyUp("win")
            except Exception as e:
                print(f"Error in hotword loop: {e}")
                break

    except Exception as e:
        print(f"Hotword initialization error: {e}")
    finally:
        # Cleanup resources
        if porcupine is not None:
            try:
                porcupine.delete()
            except Exception as e:
                print(f"Error deleting porcupine: {e}")
        
        if audio_stream is not None:
            try:
                audio_stream.close()
            except Exception as e:
                print(f"Error closing audio stream: {e}")
        
        if paud is not None:
            try:
                paud.terminate()
            except Exception as e:
                print(f"Error terminating PyAudio: {e}")

def findContact(query):
    """Find contact phone number from database"""
    try:
        words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
        query = remove_words(query, words_to_remove)

        try:
            query = query.strip().lower()
            cursor.execute("SELECT Phone FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", 
                          ('%' + query + '%', query + '%'))
            results = cursor.fetchall()
            
            if results:
                mobile_number_str = str(results[0][0])
                if not mobile_number_str.startswith('+91'):
                    mobile_number_str = '+91' + mobile_number_str
                return mobile_number_str, query
            else:
                speak('not exist in contacts')
                return 0, 0
        except Exception as e:
            print(f"Database query error: {e}")
            speak('Contact not found')
            return 0, 0
    except Exception as e:
        print(f"findContact error: {e}")
        return 0, 0

def whatsApp(Phone, message, flag, name):
    """Send WhatsApp message, call or video call"""
    try:
        if flag == 'message':
            target_tab = 12
            jarvis_message = "message send successfully to " + name
        elif flag == 'call':
            target_tab = 7
            message = ''
            jarvis_message = "calling to " + name
        else:
            target_tab = 6
            message = ''
            jarvis_message = "staring video call with " + name

        # Encode the message for URL
        encoded_message = quote(message)
        print(encoded_message)

        # Construct the URL
        whatsapp_url = f"whatsapp://send?phone={Phone}&text={encoded_message}"

        # Construct the full command
        full_command = f'start "" "{whatsapp_url}"'

        # Open WhatsApp with the constructed URL using cmd.exe
        subprocess.run(full_command, shell=True)
        time.sleep(5)
        subprocess.run(full_command, shell=True)
        pyautogui.hotkey('ctrl', 'f')

        for i in range(1, target_tab):
            pyautogui.hotkey('tab')
        
        pyautogui.hotkey('enter')
        speak(jarvis_message)
    except Exception as e:
        print(f"WhatsApp error: {e}")
        speak("Error sending WhatsApp message")

def chatBot(query):
    """Chat with HuggingChat AI"""
    try:
        user_input = query.lower()
        cookie_path = os.path.join("backend", "cookie.json")
        
        if not os.path.exists(cookie_path):
            error_msg = "Cookie file not found. Configure HuggingFace cookies in backend/cookie.json"
            speak(error_msg)
            print(f"ChatBot error: {error_msg}")
            return error_msg
        
        # Check if cookies are valid
        with open(cookie_path, 'r') as f:
            content = f.read().strip()
            if content == "[]" or not content:
                error_msg = "No cookies configured. Add your HuggingFace cookies to backend/cookie.json"
                speak(error_msg)
                print(f"ChatBot error: {error_msg}")
                return error_msg
        
        try:
            chatbot = hugchat.ChatBot(cookie_path=cookie_path)
            id = chatbot.new_conversation()
            chatbot.change_conversation(id)
            response = chatbot.chat(user_input)
            print(f"ChatBot response: {response}")
            speak(response)
            return response
        except Exception as chat_error:
            error_msg = f"HuggingChat error: {str(chat_error)}"
            print(f"ChatBot connection error: {error_msg}")
            speak("Cannot connect to HuggingChat. Please verify your cookies are valid.")
            return error_msg
            
    except Exception as e:
        error_msg = f"Unexpected error in chatBot: {str(e)}"
        print(f"ChatBot error: {error_msg}")
        speak("Error in chat response")
        return error_msg