import json
import os
import logging
import time
import re
from tqdm import tqdm
from pathlib import Path
import pandas as pd
from utils.gpt_api import translate_with_gpt
from utils.regex_rules import load_corrections, apply_corrections, validate_arabizi
from utils.variant_rules import generate_variants


def setup_logging():
    """Configure logging with directory creation."""
    log_dir = Path("D:/code-X_internship/arabizi_dataset_generator/logs")
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "main.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


# Initialize logger
logger = setup_logging()

# Config
BASE_DIR = Path("D:/code-X_internship/arabizi_dataset_generator")
INPUT_PATH = BASE_DIR / "data/raw/test.csv"
OUTPUT_PATH = BASE_DIR / "data/final/arabizi_dataset_testcsv.jsonl"
SKIPPED_PATH = BASE_DIR / "corrected/skipped_entries1.jsonl"
NUM_ENTRIES = 15
NUM_VARIANTS = 3
USE_GPT = True
API_DELAY = 2  # Seconds between GPT calls


def clean_text(text):
    """Clean text by removing unwanted characters and stripping whitespace."""
    return re.sub(r"[^\w\s.,!?']", '', text).strip()


def split_dialog(dialog):
    """Split dialog into turns based on punctuation or other delimiters."""
    if isinstance(dialog, list):
        return [clean_text(turn) for turn in dialog if clean_text(turn)]
    dialog = re.sub(r'[.!?]+\s+', '||', dialog)
    turns = [clean_text(turn) for turn in dialog.split('||') if clean_text(turn)]
    return turns


def preprocess_dataset(df):
    """Preprocess DataFrame to extract prompt-response pairs."""
    prompts = []
    responses = []

    for _, row in df.iterrows():
        try:
            dialog_turns = split_dialog(row['dialog'])
            # Pair all consecutive turns, handling odd lengths
            for i in range(len(dialog_turns) - 1):
                prompt = dialog_turns[i]
                response = dialog_turns[i + 1]
                if prompt and response:  # Skip empty turns
                    prompts.append(prompt)
                    responses.append(response)
        except KeyError as e:
            logger.error(f"Missing 'dialog' column in row: {e}")
            continue
        except Exception as e:
            logger.error(f"Error processing dialog: {e}")
            continue

    processed_df = pd.DataFrame({'prompt': prompts, 'response': responses})
    return processed_df


def load_dataset(file_path):
    """Load and preprocess dataset from CSV."""
    file_path = Path(file_path)
    try:
        if file_path.suffix == '.csv':
            df = pd.read_csv(file_path)
            processed_df = preprocess_dataset(df)
            return processed_df.to_dict(orient='records')
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except pd.errors.ParserError:
        logger.error(f"Invalid CSV format: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Failed to load dataset {file_path}: {e}")
        raise


def save_dataset(data, file_path):
    """Save dataset to JSONL file."""
    file_path = Path(file_path)
    os.makedirs(file_path.parent, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")


def apply_regex_corrections(text):
    """Apply regex corrections to text."""
    try:
        corrections = load_corrections()
        return apply_corrections(text, corrections).strip()
    except Exception as e:
        logger.error(f"Correction failed for text='{text}': {e}")
        return text


def generate_orthographic_variants(text, num_variants, seed=None):
    """Generate orthographic variants of Arabizi text."""
    try:
        return generate_variants(text, num_variants, seed=seed)
    except TypeError:
        logger.warning("generate_variants does not support num_variants/seed; using defaults")
        return generate_variants(text)[:num_variants]
    except Exception as e:
        logger.error(f"Variant generation failed for text='{text}': {e}")
        return [text] * num_variants


def main():
    # Ensure output directories exist
    for path in [OUTPUT_PATH.parent, SKIPPED_PATH.parent]:
        os.makedirs(path, exist_ok=True)

    # Step 1: Load and preprocess
    logger.info("Loading and preprocessing dataset...")
    try:
        data = load_dataset(INPUT_PATH)
        data = data[:NUM_ENTRIES]
        logger.info(f"Loaded {len(data)} prompt-response pairs from {INPUT_PATH}")
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        return

    final_data = []
    skipped_count = 0

    for item in tqdm(data, desc="Processing entries"):
        try:
            prompt_en = item.get("prompt")
            response_en = item.get("response")
            if not (prompt_en and response_en):
                raise ValueError("Empty or missing prompt/response")

            # Step 2: Translation
            if USE_GPT:
                try:
                    prompt_arabizi, response_arabizi = translate_with_gpt(prompt_en, response_en)
                    time.sleep(API_DELAY)
                except Exception as e:
                    logger.error(f"Translation failed for prompt='{prompt_en}': {e}")
                    raise
            else:
                prompt_arabizi, response_arabizi = "kifak?", "mnih, merci"
                logger.debug("Skipped GPT translation for testing")

            # Step 3: Regex correction
            prompt_arabizi = apply_regex_corrections(prompt_arabizi)
            response_arabizi = apply_regex_corrections(response_arabizi)

            # Validation
            valid_prompt = validate_arabizi(prompt_arabizi)
            valid_response = validate_arabizi(response_arabizi)
            if not (valid_prompt or valid_response):
                logger.warning(f"Invalid Arabizi: prompt='{prompt_arabizi}', response='{response_arabizi}'")
                raise ValueError("Both prompt and response are invalid Arabizi")

            # Step 4: Generate variants
            seed = hash(f"{prompt_arabizi}{response_arabizi}") % 10000
            prompt_variants = generate_orthographic_variants(prompt_arabizi, NUM_VARIANTS, seed)
            response_variants = generate_orthographic_variants(response_arabizi, NUM_VARIANTS, seed)

            variants = []
            for pv, rv in zip(prompt_variants, response_variants):
                if validate_arabizi(pv) and validate_arabizi(rv):
                    variants.append({"prompt_variant": pv, "response_variant": rv})
                else:
                    logger.warning(f"Invalid variant: prompt='{pv}', response='{rv}'")
                    with open(SKIPPED_PATH, "a", encoding='utf-8') as f:
                        json.dump({"prompt_variant": pv, "response_variant": rv, "error": "Invalid Arabizi"},
                                  f, ensure_ascii=False)
                        f.write("\n")

            if not variants:
                variants = [{"prompt_variant": prompt_arabizi, "response_variant": response_arabizi}]
                logger.warning(f"No valid variants for prompt='{prompt_arabizi}', response='{response_arabizi}'")

            final_data.append({
                "original": {
                    "prompt_en": prompt_en,
                    "response_en": response_en,
                    "prompt_arabizi": prompt_arabizi,
                    "response_arabizi": response_arabizi
                },
                "variants": variants
            })

        except ValueError as e:
            skipped_count += 1
            logger.error(f"Validation error: {e}")
            with open(SKIPPED_PATH, "a", encoding='utf-8') as f:
                json.dump({"item": item, "error": str(e)}, f, ensure_ascii=False)
                f.write("\n")
        except KeyError as e:
            skipped_count += 1
            logger.error(f"Missing key in entry: {e}")
            with open(SKIPPED_PATH, "a", encoding='utf-8') as f:
                json.dump({"item": item, "error": f"Missing key: {e}"}, f, ensure_ascii=False)
                f.write("\n")
        except Exception as e:
            skipped_count += 1
            logger.error(f"Error processing entry: {e}")
            with open(SKIPPED_PATH, "a", encoding='utf-8') as f:
                json.dump({"item": item, "error": str(e)}, f, ensure_ascii=False)
                f.write("\n")

    # Step 5: Save results
    logger.info(f"Processed {len(final_data)} entries, skipped {skipped_count}")
    try:
        save_dataset(final_data, OUTPUT_PATH)
        logger.info(f"Saved results to {OUTPUT_PATH}")
    except Exception as e:
        logger.error(f"Failed to save dataset: {e}")


if __name__ == "__main__":
    main()