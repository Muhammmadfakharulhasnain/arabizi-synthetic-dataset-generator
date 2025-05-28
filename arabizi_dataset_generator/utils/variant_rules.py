import random
import json
import os
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_variant_map(file_path="D:/code-X_internship/arabizi_dataset_generator/data/config/variants.json"):
    """
    Load variant mapping from a JSON file.
    Returns a dictionary of {pattern: [alternatives]}.
    """
    default_map = {
        "ee": ["i", "e"],
        "oo": ["u", "ou"],
        "3": ["a"],
        "7": ["h"],
        "2": ["a", "'"],
        "sh": ["ch", "sh"]
    }
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                variant_map = json.load(f)
            logger.info(f"Loaded {len(variant_map)} variant rules from {file_path}")
            return variant_map
        except Exception as e:
            logger.error(f"Failed to load variants from {file_path}: {e}")
    logger.warning("Using default variant map")
    return default_map


def generate_variants(text, seed=None):
    """
    Generate two random variants of the input text using variant map.
    Returns a list of two variant strings.
    """
    if not text:
        return [text, text]

    variants = []
    variant_map = load_variant_map()

    # Set seed for reproducibility
    if seed is not None:
        random.seed(seed)

    for _ in range(2):
        var = text
        for pattern, alternatives in variant_map.items():
            # Case-insensitive replacement
            try:
                def replace_match(match):
                    return random.choice(alternatives)

                var = re.sub(pattern, replace_match, var, flags=re.IGNORECASE)
            except re.error as e:
                logger.error(f"Invalid regex pattern '{pattern}': {e}")
                continue
        variants.append(var)

    # Reset seed
    random.seed(None)
    return variants


def validate_arabizi(text):
    """
    Basic validation for Arabizi text.
    Returns True if text contains Arabizi-specific characters, False otherwise.
    """
    if not text:
        return False
    pattern = r'[37shkhgh2]'
    return bool(re.search(pattern, text, re.IGNORECASE))