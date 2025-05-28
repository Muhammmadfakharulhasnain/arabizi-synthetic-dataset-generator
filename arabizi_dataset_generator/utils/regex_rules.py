import re
import json
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_corrections(file_path="D:/code-X_internship/arabizi_dataset_generator/data/config/corrections.json"):
    """
    Load regex correction rules from a JSON file.
    Returns a dictionary of {pattern: replacement}.
    """
    default_corrections = {
        r"\bmnee7\b": "mnih",
        r"\bkeef\b": "kif",
        r"\bmasi\b": "merci",
        r"\bshokr\b": "shoukran",
        r"\bana\b": "ana",
    }
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                corrections = json.load(f)
            logger.info(f"Loaded {len(corrections)} corrections from {file_path}")
            return corrections
        except Exception as e:
            logger.error(f"Failed to load corrections from {file_path}: {e}")
    logger.warning("Using default corrections")
    return default_corrections

def apply_corrections(text, corrections_dict):
    """
    Apply regex corrections to text using the provided corrections dictionary.
    Returns corrected text.
    """
    if not text:
        return text
    original_text = text
    for pattern, repl in corrections_dict.items():
        try:
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
        except re.error as e:
            logger.error(f"Invalid regex pattern '{pattern}': {e}")
            continue
    if text != original_text:
        logger.debug(f"Applied corrections: '{original_text}' -> '{text}'")
    return text

def validate_arabizi(text):
    """
    Basic validation for Arabizi text.
    Returns True if text contains Arabizi-specific characters, False otherwise.
    """
    if not text:
        return False
    pattern = r'[37shkhgh2]'
    return bool(re.search(pattern, text, re.IGNORECASE))