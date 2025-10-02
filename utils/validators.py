
# ============================================
# utils/validators.py
# ============================================
import re
from typing import List

def clean_text(text: str) -> str:
    """
    Clean and normalize text input.
    
    Args:
        text: Raw text input
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\-.,!?\'\"()]', '', text)
    
    return text

def extract_keywords(text: str, keyword_list: List[str]) -> List[str]:
    """
    Extract matching keywords from text.
    
    Args:
        text: Input text
        keyword_list: List of keywords to search for
        
    Returns:
        List of found keywords
    """
    if not text:
        return []
    
    text_lower = text.lower()
    found_keywords = [kw for kw in keyword_list if kw.lower() in text_lower]
    
    return found_keywords
