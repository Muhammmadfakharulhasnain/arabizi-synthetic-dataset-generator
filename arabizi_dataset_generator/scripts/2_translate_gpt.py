import json
import os
import ijson
from utils.gpt_api import translate_with_gpt
import logging
from tqdm import tqdm

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # File paths (relative to script location)
    input_path = "../data/translated/preprocessed.json"
    output_path = "../data/translated/translated1.json"
    skipped_path = "../data/corrected/skipped_entries.jsonl"

    # Load only the first 15 entries
    data = []
    try:
        with open(input_path, 'rb') as f:
            parser = ijson.items(f, 'item')
            for i, entry in enumerate(parser):
                if i >= 15:
                    break
                data.append(entry)
        logger.info(f"Loaded {len(data)} entries from {input_path}")
    except FileNotFoundError:
        logger.error(f"Input file not found: {input_path}")
        return
    except ijson.JSONError:
        logger.error(f"Invalid JSON in {input_path}")
        return

    if not data:
        logger.error("No entries loaded from input file")
        return

    output = []
    # Process entries with progress bar
    for entry in tqdm(data, desc="Translating entries"):
        try:
            prompt, response = entry["prompt"], entry["response"]
            arabizi_prompt, arabizi_response = translate_with_gpt(prompt, response)
            entry["prompt_arabizi"] = arabizi_prompt
            entry["response_arabizi"] = arabizi_response
            output.append(entry)
        except KeyError as e:
            logger.error(f"Missing key in entry: {e}. Skipping.")
            with open(skipped_path, "a", encoding='utf-8') as f:
                json.dump({"prompt": entry.get("prompt"), "response": entry.get("response"),
                           "error": f"Missing key: {e}"}, f, ensure_ascii=False)
                f.write("\n")
            continue
        except Exception as e:
            logger.error(f"Unexpected error for entry: {e}. Skipping.")
            with open(skipped_path, "a", encoding='utf-8') as f:
                json.dump({"prompt": prompt, "response": response, "error": str(e)}, f, ensure_ascii=False)
                f.write("\n")
            continue

    # Save translated data
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(output)} entries to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save output: {e}")

if __name__ == "__main__":
    main()
