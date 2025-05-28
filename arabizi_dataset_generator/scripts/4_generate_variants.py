import json
import os
import logging
from tqdm import tqdm
from utils.variant_rules import generate_variants, validate_arabizi

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # File paths
    input_path = "D:/code-X_internship/arabizi_dataset_generator/data/corrected/Regex_cleaned.json"
    output_path = "D:/code-X_internship/arabizi_dataset_generator/data/final/arabizi_dataset.json"
    skipped_path = "D:/code-X_internship/arabizi_dataset_generator/data/corrected/skipped_entries.jsonl"

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

    # Process entries
    output = []
    for entry in tqdm(data, desc="Generating variants"):
        try:
            prompt_arabizi = entry.get("prompt_arabizi", "").strip()
            response_arabizi = entry.get("response_arabizi", "").strip()

            # Generate variants with consistent seed
            seed = hash(prompt_arabizi + response_arabizi) % 10000
            prompt_variants = generate_variants(prompt_arabizi, seed=seed)
            response_variants = generate_variants(response_arabizi, seed=seed)

            # Validate variants
            valid_variants = []
            for v1, v2 in zip(prompt_variants, response_variants):
                if validate_arabizi(v1) and validate_arabizi(v2):
                    valid_variants.append({"prompt_variant": v1, "response_variant": v2})
                else:
                    logger.warning(f"Invalid variant: prompt='{v1}', response='{v2}'")
                    with open(skipped_path, "a", encoding='utf-8') as f:
                        json.dump({"prompt_variant": v1, "response_variant": v2, "error": "Invalid Arabizi"},
                                  f, ensure_ascii=False)
                        f.write("\n")

            entry["variants"] = valid_variants if valid_variants else [
                {"prompt_variant": prompt_arabizi, "response_variant": response_arabizi}
            ]
            output.append(entry)
        except Exception as e:
            logger.error(f"Error processing entry: {e}. Skipping.")
            with open(skipped_path, "a", encoding='utf-8') as f:
                json.dump({"entry": entry, "error": str(e)}, f, ensure_ascii=False)
                f.write("\n")
            continue

    # Save output data
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(output)} entries to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save output: {e}")

if __name__ == "__main__":
    main()