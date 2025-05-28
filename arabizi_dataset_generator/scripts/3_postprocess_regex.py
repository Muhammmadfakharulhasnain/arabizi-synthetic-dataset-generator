import json
import os
import logging
from tqdm import tqdm
from utils.regex_rules import load_corrections, apply_corrections, validate_arabizi

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # File paths
    input_path = "D:/code-X_internship/arabizi_dataset_generator/data/translated/translated1.json"
    output_path = "D:/code-X_internship/arabizi_dataset_generator/data/corrected/Regex_cleaned.json"
    skipped_path = "D:/code-X_internship/arabizi_dataset_generator/data/corrected/skipped_postprocess.jsonl"

    # Load input data
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data)} entries from {input_path}")
    except FileNotFoundError:
        logger.error(f"Input file not found: {input_path}")
        return
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in {input_path}")
        return

    # Load corrections
    corrections = load_corrections()

    # Process entries
    output = []
    for entry in tqdm(data, desc="Post-processing entries"):
        try:
            prompt_arabizi = entry.get("prompt_arabizi", "")
            response_arabizi = entry.get("response_arabizi", "")

            # Apply corrections
            corrected_prompt = apply_corrections(prompt_arabizi, corrections)
            corrected_response = apply_corrections(response_arabizi, corrections)

            # Validate Arabizi
            if not validate_arabizi(corrected_prompt) or not validate_arabizi(corrected_response):
                logger.warning(f"Invalid Arabizi in entry: prompt='{corrected_prompt}', response='{corrected_response}'")
                with open(skipped_path, "a", encoding='utf-8') as f:
                    json.dump({"prompt_arabizi": corrected_prompt, "response_arabizi": corrected_response,
                               "error": "Invalid Arabizi"}, f, ensure_ascii=False)
                    f.write("\n")
                entry["prompt_arabizi"] = corrected_prompt
                entry["response_arabizi"] = corrected_response
                output.append(entry)
                continue

            entry["prompt_arabizi"] = corrected_prompt
            entry["response_arabizi"] = corrected_response
            output.append(entry)
        except Exception as e:
            logger.error(f"Error processing entry: {e}. Skipping.")
            with open(skipped_path, "a", encoding='utf-8') as f:
                json.dump({"entry": entry, "error": str(e)}, f, ensure_ascii=False)
                f.write("\n")
            continue

    # Save cleaned data
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(output)} entries to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save output: {e}")

if __name__ == "__main__":
    main()
