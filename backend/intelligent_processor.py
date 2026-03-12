"""
Intelligent Command Processor with Fuzzy Matching
Understands commands in multiple languages and variants
"""

from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Optional
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommandProcessor:
    """Process commands with intelligent understanding"""
    
    def __init__(self):
        self.command_patterns = self.load_command_patterns()
        self.context = {}
        self.last_command = None
    
    def load_command_patterns(self) -> Dict:
        """Load command patterns from configuration"""
        return {
            'open_app': {
                'en': ['open', 'launch', 'start', 'run', 'execute'],
                'hi': ['खोलो', 'शुरू करो', 'चलाओ'],
                'mr': ['उघडा', 'सुरू करा', 'चला']
            },
            'youtube': {
                'en': ['play', 'youtube', 'search', 'video', 'watch'],
                'hi': ['खेलो', 'यूट्यूब', 'खोजो', 'देखो'],
                'mr': ['वाजवा', 'यूट्यूब', 'शोधा', 'बघा']
            },
            'whatsapp': {
                'en': ['send', 'message', 'call', 'whatsapp', 'video call'],
                'hi': ['भेजो', 'संदेश', 'कॉल', 'व्हाट्सअप'],
                'mr': ['पाठवा', 'संदेश', 'कॉल', 'व्हाट्सअप']
            },
            'weather': {
                'en': ['weather', 'temperature', 'climate', 'forecast'],
                'hi': ['मौसम', 'तापमान', 'जलवायु'],
                'mr': ['हवामान', 'तापमान', 'हवामानाचा']
            },
            'time': {
                'en': ['time', 'clock', 'hour', 'what time'],
                'hi': ['समय', 'घड़ी', 'कितना बजा'],
                'mr': ['वेळ', 'घड़ी', 'किती वाजले']
            },
            'date': {
                'en': ['date', 'day', 'calendar', 'today'],
                'hi': ['तारीख', 'दिन', 'आज'],
                'mr': ['तारीख', 'दिवस', 'आज']
            },
            'search': {
                'en': ['search', 'find', 'look for', 'google'],
                'hi': ['खोजो', 'ढूंढो'],
                'mr': ['शोधा', 'शोध']
            },
            'language': {
                'en': ['language', 'change language', 'speak', 'hindi', 'marathi', 'english'],
                'hi': ['भाषा', 'हिंदी', 'मराठी', 'अंग्रेजी'],
                'mr': ['भाषा', 'हिंदी', 'मराठी', 'इंग्रजी']
            }
        }
    
    def calculate_similarity(self, input_text: str, pattern: str) -> float:
        """Calculate similarity between input and pattern"""
        input_lower = input_text.lower()
        pattern_lower = pattern.lower()
        
        # Check if pattern is substring
        if pattern_lower in input_lower:
            return 0.9
        
        # Use SequenceMatcher for fuzzy matching
        return SequenceMatcher(None, input_lower, pattern_lower).ratio()
    
    def identify_command_type(self, text: str, language: str = 'en') -> Tuple[Optional[str], float]:
        """Identify command type from text"""
        best_match = None
        best_score = 0.5  # Minimum threshold
        
        for command_type, patterns in self.command_patterns.items():
            lang_patterns = patterns.get(language, [])
            
            for pattern in lang_patterns:
                score = self.calculate_similarity(text, pattern)
                
                if score > best_score:
                    best_score = score
                    best_match = command_type
        
        return best_match, best_score
    
    def extract_entity(self, text: str, entity_type: str) -> Optional[str]:
        """Extract entity from command (e.g., app name, contact name)"""
        # Remove common stop words
        stop_words = ['open', 'launch', 'play', 'send', 'call', 'the', 'to', 'on']
        words = [w for w in text.split() if w.lower() not in stop_words]
        
        if words:
            return ' '.join(words)
        return None
    
    def understand_intent(self, text: str, language: str = 'en') -> Dict:
        """Understand user intent from command"""
        command_type, confidence = self.identify_command_type(text, language)
        entity = self.extract_entity(text, command_type) if command_type else None
        
        return {
            'type': command_type,
            'confidence': confidence,
            'entity': entity,
            'original_text': text,
            'language': language,
            'full_understanding': f"{command_type}: {entity}" if entity else command_type
        }
    
    def update_context(self, command_type: str, entity: str):
        """Update conversation context"""
        self.context['last_command'] = command_type
        self.context['last_entity'] = entity
        self.last_command = command_type
    
    def get_context(self) -> Dict:
        """Get current conversation context"""
        return self.context.copy()
    
    def generate_jarvis_response(self, command_type: str, entity: str, language: str = 'en') -> str:
        """Generate Jarvis-style response"""
        responses = {
            'en': {
                'open_app': f"Opening {entity}, sir.",
                'youtube': f"Playing {entity} on YouTube, sir.",
                'whatsapp': f"Sending to {entity}, sir.",
                'weather': "Checking the weather for you, sir.",
                'time': "Checking the time, sir.",
                'date': "Today's date is available, sir.",
                'search': f"Searching for {entity}, sir.",
                'language': f"Changing language, sir.",
            },
            'hi': {
                'open_app': f"{entity} खोल रहा हूं, सर।",
                'youtube': f"यूट्यूब पर {entity} चला रहा हूं, सर।",
                'whatsapp': f"{entity} को भेज रहा हूं, सर।",
                'weather': "मौसम देख रहा हूं, सर।",
                'time': "समय देख रहा हूं, सर।",
                'date': "तारीख देख रहा हूं, सर।",
                'search': f"{entity} ढूंढ रहा हूं, सर।",
                'language': "भाषा बदल रहा हूं, सर।",
            },
            'mr': {
                'open_app': f"{entity} उघडत आहे, सर।",
                'youtube': f"यूट्यूबवर {entity} वाजवत आहे, सर।",
                'whatsapp': f"{entity} ला पाठवत आहे, सर।",
                'weather': "हवामान बघत आहे, सर।",
                'time': "वेळ बघत आहे, सर।",
                'date': "तारीख बघत आहे, सर।",
                'search': f"{entity} शोधत आहे, सर।",
                'language': "भाषा बदलत आहे, सर।",
            }
        }
        
        lang_responses = responses.get(language, responses['en'])
        return lang_responses.get(command_type, f"Processing your request, sir.")
    
    def get_jarvis_wit(self, language: str = 'en') -> str:
        """Get Jarvis-style witty responses"""
        wit = {
            'en': [
                "At your service, sir.",
                "I'm prepared for this, sir.",
                "Very good, sir.",
                "Right away, sir.",
                "As you wish, sir.",
                "Processing, sir.",
            ],
            'hi': [
                "आपकी सेवा में, सर।",
                "बिल्कुल, सर।",
                "तुरंत, सर।",
                "जी, सर।",
            ],
            'mr': [
                "आपल्या सेवेत, सर।",
                "नक्की, सर।",
                "लगेच, सर।",
                "होय, सर।",
            ]
        }
        
        import random
        lang_wit = wit.get(language, wit['en'])
        return random.choice(lang_wit)
