"""
Helper module - Utility functions
Provides helper functions for text processing and extraction
"""

import re
from typing import Optional, List


def extract_yt_term(command: str) -> Optional[str]:
    """
    Extract the YouTube search term from a voice command
    
    Args:
        command: The voice command text
        
    Returns:
        The search term or None if not found
        
    Examples:
        "play taylor swift on youtube" -> "taylor swift"
        "play on youtube" -> None
    """
    try:
        # Pattern to match 'play <term> on youtube'
        pattern = r'play\s+(.*?)\s+on\s+youtube'
        match = re.search(pattern, command, re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        # Fallback pattern: just 'play <anything>' if 'youtube' is in command
        if 'youtube' in command.lower():
            fallback_pattern = r'play\s+(.*?)(?:\s+on\s+youtube)?$'
            match = re.search(fallback_pattern, command, re.IGNORECASE)
            if match:
                term = match.group(1).strip()
                if term.lower() not in ['on', 'youtube']:
                    return term
        
        return None
        
    except Exception as e:
        print(f"Error in extract_yt_term: {str(e)}")
        return None


def remove_words(input_string: str, words_to_remove: List[str]) -> str:
    """
    Remove specified words from a string
    
    Args:
        input_string: The input text
        words_to_remove: List of words to remove (case-insensitive)
        
    Returns:
        String with specified words removed
        
    Examples:
        remove_words("jarvis open google chrome", ["jarvis", "open"])
        -> "google chrome"
    """
    try:
        if not input_string:
            return ""
        
        # Split the string into words
        words = input_string.split()
        
        # Create a lowercase version of words to remove for comparison
        words_lower = [word.lower() for word in words_to_remove]
        
        # Filter out words that are in the removal list
        filtered_words = [
            word for word in words 
            if word.lower() not in words_lower
        ]
        
        # Join the remaining words back together
        result = ' '.join(filtered_words)
        return result.strip()
        
    except Exception as e:
        print(f"Error in remove_words: {str(e)}")
        return input_string


def clean_command(command: str, assistant_name: str = "jarvis") -> str:
    """
    Clean and normalize a voice command
    
    Args:
        command: The voice command text
        assistant_name: The name of the assistant (for removal)
        
    Returns:
        Cleaned command text
    """
    try:
        # Convert to lowercase
        command = command.lower().strip()
        
        # Remove the assistant name
        command = command.replace(assistant_name, "").strip()
        
        # Remove extra whitespace
        command = ' '.join(command.split())
        
        return command
        
    except Exception as e:
        print(f"Error in clean_command: {str(e)}")
        return command


def extract_phone_number(text: str) -> Optional[str]:
    """
    Extract phone number from text
    
    Args:
        text: Text containing phone number
        
    Returns:
        Extracted phone number or None
        
    Examples:
        "call 9876543210" -> "9876543210"
        "my number is +919876543210" -> "9876543210"
    """
    try:
        # Pattern for Indian phone numbers
        patterns = [
            r'\+91[\s]?(\d{10})',  # +91 format
            r'91[\s]?(\d{10})',     # 91 format
            r'0[\s]?(\d{10})',      # 0 format
            r'(?:^|\D)(\d{10})(?:\D|$)',  # 10 digit number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                phone = match.group(1) if '(' in pattern else match.group(0)
                # Return only digits
                phone = re.sub(r'\D', '', phone)
                if len(phone) == 10:
                    return phone
        
        return None
        
    except Exception as e:
        print(f"Error in extract_phone_number: {str(e)}")
        return None


def validate_command(command: str) -> bool:
    """
    Validate if a command is valid
    
    Args:
        command: The command text to validate
        
    Returns:
        True if valid, False otherwise
    """
    return isinstance(command, str) and len(command.strip()) > 0