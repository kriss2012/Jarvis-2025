"""
Jarvis Personality Module
Adds personality, wit, and natural responses like the real Jarvis from Iron Man
"""

import random
import time
import logging
from typing import Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JarvisPersonality:
    """Adds personality to Jarvis like the movie character"""
    
    def __init__(self, name: str = "Jarvis"):
        self.name = name
        self.interactions = 0
        self.user_name = "Sir"
        self.mood = "professional"  # professional, witty, humorous
        self.startup_done = False
    
    def set_user_name(self, name: str):
        """Set the user's name for personalization"""
        self.user_name = name
    
    def get_greeting(self, language: str = 'en', hour: Optional[int] = None) -> str:
        """Get time-appropriate greeting"""
        if hour is None:
            hour = datetime.now().hour
        
        greetings = {
            'en': {
                'morning': f"Good morning, {self.user_name}. I trust you slept well.",
                'afternoon': f"Good afternoon, {self.user_name}. I hope you're having a productive day.",
                'evening': f"Good evening, {self.user_name}. The day is winding down.",
                'night': f"Good evening, {self.user_name}. It's quite late.",
                'startup': f"Good morning, {self.user_name}. I am now online and ready to assist."
            },
            'hi': {
                'morning': f"सुप्रभात, {self.user_name}। मुझे आशा है आप अच्छे से सोए हैं।",
                'afternoon': f"शुभ अपराह्न, {self.user_name}। आप एक उत्पादक दिन बिता रहे हैं।",
                'evening': f"शुभ संध्या, {self.user_name}। दिन समाप्त हो रहा है।",
                'night': f"शुभ रात्रि, {self.user_name}। बहुत देर हो गई है।",
                'startup': f"नमस्ते, {self.user_name}। मैं अब ऑनलाइन हूं।"
            },
            'mr': {
                'morning': f"सुप्रभातम्, {self.user_name}। तुम्ही चांगले झोपलात असण्याची आशा करतो.",
                'afternoon': f"शुभ अपराह्न, {self.user_name}। तुम्ही एक उत्पादक दिवस मिळवत आहात.",
                'evening': f"शुभ संध्या, {self.user_name}। दिवस संपत आहे.",
                'night': f"शुभ रात्री, {self.user_name}। खूप मध्यरात्री झाली.",
                'startup': f"नमस्कार, {self.user_name}। मी आता ऑनलाइन आहे।"
            }
        }
        
        lang_greetings = greetings.get(language, greetings['en'])
        
        if hour < 12:
            greeting_type = 'morning'
        elif hour < 17:
            greeting_type = 'afternoon'
        elif hour < 21:
            greeting_type = 'evening'
        else:
            greeting_type = 'night'
        
        return lang_greetings.get(greeting_type, lang_greetings['morning'])
    
    def get_startup_message(self, language: str = 'en') -> str:
        """Get startup message"""
        startup_msgs = {
            'en': [
                "I am now online.",
                "Systems online.",
                "I'm ready to assist, sir.",
                "All systems operational.",
            ],
            'hi': [
                "मैं अब ऑनलाइन हूं।",
                "सिस्टम ऑनलाइन है।",
                "मैं आपकी मदद के लिए तैयार हूं।",
            ],
            'mr': [
                "मी आता ऑनलाइन आहे।",
                "सिस्टम ऑनलाइन आहे।",
                "मी तुम्हाला मदत करण्यासाठी तयार आहे।",
            ]
        }
        
        msgs = startup_msgs.get(language, startup_msgs['en'])
        return random.choice(msgs)
    
    def get_confirmation(self, language: str = 'en', custom_msg: Optional[str] = None) -> str:
        """Get confirmation messages"""
        confirmations = {
            'en': [
                "Very good, sir.",
                "At your service, sir.",
                "Right away, sir.",
                "As you wish, sir.",
                "Understood, sir.",
                "I'm on it, sir.",
                "Processing, sir.",
            ],
            'hi': [
                "बहुत अच्छे, सर।",
                "आपकी सेवा में, सर।",
                "तुरंत, सर।",
                "जैसा आप चाहें, सर।",
                "समझा, सर।",
                "मैं इस पर काम कर रहा हूं।",
            ],
            'mr': [
                "खूपच चांगले, सर।",
                "आपल्या सेवेत, सर।",
                "लगेच, सर।",
                "जसे तुम्हाला हवे, सर।",
                "समजले, सर।",
                "मी यावर काम करत आहे।",
            ]
        }
        
        if custom_msg:
            return custom_msg
        
        msgs = confirmations.get(language, confirmations['en'])
        return random.choice(msgs)
    
    def get_apology(self, language: str = 'en', error: Optional[str] = None) -> str:
        """Get apology messages for errors"""
        apologies = {
            'en': [
                "I apologize, sir. I'm unable to complete that request.",
                "I'm afraid I cannot do that, sir.",
                "My sincerest apologies, sir.",
                "I regret to inform you, sir.",
            ],
            'hi': [
                "मुझे खेद है, सर। मैं वह अनुरोध पूरा नहीं कर सकता।",
                "मुझे डर है, मैं ऐसा नहीं कर सकता, सर।",
                "मुझे खेद है, सर।",
            ],
            'mr': [
                "मुझे खेद आहे, सर। मी ते पूर्ण करू शकत नाही।",
                "मुझे भय आहे, मी ते करू शकत नाही, सर।",
                "माझे खेद, सर।",
            ]
        }
        
        msgs = apologies.get(language, apologies['en'])
        return random.choice(msgs)
    
    def get_status_update(self, language: str = 'en', action: str = "processing") -> str:
        """Get status updates"""
        updates = {
            'en': {
                'processing': f"I'm processing that request, sir.",
                'complete': f"Task completed successfully, sir.",
                'searching': f"Searching now, sir.",
                'connecting': f"Establishing connection, sir.",
                'waiting': f"Awaiting your command, sir.",
            },
            'hi': {
                'processing': f"मैं उस अनुरोध को संसाधित कर रहा हूं।",
                'complete': f"कार्य सफलतापूर्वक पूरा हुआ।",
                'searching': f"अभी खोज रहा हूं।",
                'connecting': f"कनेक्शन स्थापित कर रहा हूं।",
                'waiting': f"आपके आदेश की प्रतीक्षा है।",
            },
            'mr': {
                'processing': f"मी ते विनंती प्रक्रिया करत आहे।",
                'complete': f"कार्य यशस्वीरित्या पूर्ण झाले।",
                'searching': f"आता शोधत आहे।",
                'connecting': f"कनेक्शन स्थापित करत आहे।",
                'waiting': f"तुमच्या आदेशाची प्रतीक्षा करत आहे।",
            }
        }
        
        lang_updates = updates.get(language, updates['en'])
        return lang_updates.get(action, lang_updates['processing'])
    
    def get_farewell(self, language: str = 'en') -> str:
        """Get farewell messages"""
        farewells = {
            'en': [
                "Thank you, sir. Until next time.",
                "Very good, sir. I shall await your next instruction.",
                "It has been a pleasure, sir.",
                "I shall be here when you need me, sir.",
            ],
            'hi': [
                "धन्यवाद, सर। अगली बार तक।",
                "बहुत अच्छे, सर। मैं आपके अगले आदेश की प्रतीक्षा करता हूं।",
                "यह एक सुख रहा, सर।",
                "मैं तब यहां होऊंगा जब आपको मेरी आवश्यकता हो।",
            ],
            'mr': [
                "धन्यवाद, सर। पुढच्या वेळेपर्यंत।",
                "खूपच चांगले, सर। मी तुमच्या पुढच्या आदेशाची प्रतीक्षा करत आहे।",
                "हे आनंदाची गोष्ट होती, सर।",
                "जेव्हा तुम्हाला मेरी गरज असेल तेव्हा मी येथे असेन।",
            ]
        }
        
        msgs = farewells.get(language, farewells['en'])
        return random.choice(msgs)
    
    def get_witty_response(self, language: str = 'en') -> str:
        """Get witty Jarvis responses"""
        witty = {
            'en': [
                "I'm afraid that's beyond my current capabilities, sir.",
                "That would be rather inadvisable, sir.",
                "I would advise against that, sir.",
                "Your request is noted, sir.",
                "Quite right, sir.",
            ],
            'hi': [
                "मुझे डर है कि यह मेरी वर्तमान क्षमताओं से परे है।",
                "यह काफी अनुचित होगा।",
                "मैं इसके विरुद्ध सलाह दूंगा।",
            ],
            'mr': [
                "मुझे भय आहे हे माझ्या सामर्थ्याच्या बाहेर आहे।",
                "हे अत्यंत अनुचित असेल।",
                "मी याच्या विरुद्ध सल्ला दिईन।",
            ]
        }
        
        msgs = witty.get(language, witty['en'])
        return random.choice(msgs)
    
    def increment_interactions(self):
        """Track number of interactions"""
        self.interactions += 1
        if self.interactions % 10 == 0:
            logger.info(f"Jarvis: {self.interactions} interactions completed.")
    
    def get_intelligence_update(self, language: str = 'en') -> str:
        """Get update on system intelligence"""
        updates = {
            'en': f"I have processed {self.interactions} commands today, sir.",
            'hi': f"मैंने आज {self.interactions} आदेशों को संसाधित किया है।",
            'mr': f"मी आज {self.interactions} आदेश प्रक्रिया केले आहेत।",
        }
        return updates.get(language, updates['en'])
