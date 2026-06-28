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
        active_name = get_active_persona().lower()
        query = query.replace(active_name, "").replace("jarvis", "").replace("friday", "")
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
        active_name = get_active_persona().lower()
        words_to_remove = [active_name, 'jarvis', 'friday', 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
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

def query_offline_ollama(query):
    """Query the local offline Ollama model"""
    import subprocess
    import requests
    import time
    
    ollama_url = "http://127.0.0.1:11434"
    model_name = "gemma-heretic-local"
    ollama_path = "G:\\Shared\\bin\\ollama-windows.exe"
    modelfile_path = "G:\\Shared\\models\\Modelfile"
    
    # 1. Check if Ollama is running
    is_running = False
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=2)
        if response.status_code == 200:
            is_running = True
    except Exception:
        pass
        
    # 2. Try starting it if not running
    if not is_running:
        if os.path.exists(ollama_path):
            print("Ollama is not running. Starting local Ollama server...")
            try:
                env = os.environ.copy()
                env["OLLAMA_MODELS"] = "G:\\Shared\\models\\ollama_data"
                subprocess.Popen([ollama_path, "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
                # Wait for server to boot
                for _ in range(6):
                    time.sleep(1)
                    try:
                        resp = requests.get(f"{ollama_url}/api/tags", timeout=1)
                        if resp.status_code == 200:
                            is_running = True
                            break
                    except Exception:
                        pass
            except Exception as e:
                print(f"Failed to start Ollama process: {e}")
        else:
            print("Local Ollama executable not found at G:\\Shared\\bin\\ollama-windows.exe")
            
    if not is_running:
        return None
        
    # 3. Verify if model is loaded/registered
    try:
        tags_resp = requests.get(f"{ollama_url}/api/tags", timeout=2).json()
        models = [m["name"] for m in tags_resp.get("models", [])]
        has_model = any(model_name in m for m in models)
        
        if not has_model:
            if os.path.exists(ollama_path) and os.path.exists(modelfile_path):
                print(f"Model {model_name} not found. Creating model from Modelfile...")
                env = os.environ.copy()
                env["OLLAMA_MODELS"] = "G:\\Shared\\models\\ollama_data"
                subprocess.run([ollama_path, "create", model_name, "-f", "Modelfile"], 
                               cwd="G:\\Shared\\models", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
            else:
                print("Cannot create model: Modelfile or Ollama executable missing.")
    except Exception as e:
        print(f"Error checking or creating model: {e}")
        
    # 4. Run inference
    try:
        persona = get_active_persona()
        if persona.lower() == "friday":
            system_prompt = "You are Friday, a highly efficient, modern, and loyal AI assistant like the one from Iron Man. Keep replies brief, conversational, and direct."
        else:
            system_prompt = "You are Jarvis, a brilliant, witty, and loyal AI assistant like the one from Iron Man. Keep replies brief, conversational, and direct."
            
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {"role": "user", "content": query}
            ],
            "stream": False
        }
        
        headers = {"Content-Type": "application/json"}
        resp = requests.post(f"{ollama_url}/api/chat", json=payload, headers=headers, timeout=30)
        
        if resp.status_code == 200:
            result = resp.json()
            return result.get("message", {}).get("content", "")
    except Exception as e:
        print(f"Ollama inference error: {e}")
        
    return None

def get_active_persona():
    """Retrieve the active persona from persona_config.json"""
    import json
    import os
    config_path = os.path.join("backend", "persona_config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config.get("persona", "Jarvis")
        except Exception:
            return "Jarvis"
    return "Jarvis"

def chatBot(query):
    """Persona-aware Hybrid Online/Offline Chatbot:
    - Friday: Online priority, falls back to offline.
    - Jarvis: Offline priority, falls back to online.
    """
    user_input = query.lower()
    persona = get_active_persona().lower()
    is_friday = (persona == "friday")
    
    def run_online():
        cookie_path = os.path.join("backend", "cookie.json")
        if os.path.exists(cookie_path):
            try:
                with open(cookie_path, 'r') as f:
                    content = f.read().strip()
                if content and content != "[]":
                    print("Attempting online query via HuggingChat...")
                    chatbot = hugchat.ChatBot(cookie_path=cookie_path)
                    id = chatbot.new_conversation()
                    chatbot.change_conversation(id)
                    online_response = chatbot.chat(user_input)
                    return online_response
            except Exception as e:
                print(f"Online attempt failed: {e}")
        return None

    def run_offline():
        print("Attempting offline query via local Ollama...")
        return query_offline_ollama(query)

    if is_friday:
        # Friday: Online first, offline fallback
        print("Friday active: prioritizing online cloud layers...")
        resp = run_online()
        if resp:
            print(f"Friday (Online) response: {resp}")
            speak(resp)
            return resp
        
        print("Friday online failed. Falling back to local core...")
        speak("Cloud link down, boss. Accessing offline backup...")
        resp = run_offline()
        if resp:
            print(f"Friday (Offline fallback) response: {resp}")
            speak(resp)
            return resp
    else:
        # Jarvis: Offline first, online fallback
        print("Jarvis active: prioritizing offline local core...")
        resp = run_offline()
        if resp:
            print(f"Jarvis (Offline) response: {resp}")
            speak(resp)
            return resp
            
        print("Jarvis offline failed. Falling back to cloud layers...")
        speak("Local database offline, sir. Reconnecting to cloud satellite backup...")
        resp = run_online()
        if resp:
            print(f"Jarvis (Online fallback) response: {resp}")
            speak(resp)
            return resp

    # Both failed
    if is_friday:
        err = "I am sorry, boss. Both the satellite connection and local backup cores are unresponsive."
    else:
        err = "My apologies, sir. I am unable to connect to either my local database or cloud relay satellites."
    speak(err)
    return err