import pandas as pd
import re
import os

def clean_text(text):
    """Clean text by removing unwanted characters and stripping whitespace."""
    return re.sub(r"[^\w\s.,!?']", '', text).strip()

def split_dialog(dialog):
    """Split dialog into turns based on punctuation or other delimiters."""
    # If dialog is already a list, return it
    if isinstance(dialog, list):
        return dialog
    # Replace common delimiters with a unique separator (e.g., '||')
    dialog = re.sub(r'[.!?]+\s+', '||', dialog)
    # Split into turns and clean each turn
    turns = [clean_text(turn) for turn in dialog.split('||') if turn.strip()]
    return turns

def preprocess_dataset(input_path):
    """Preprocess DailyDialog CSV dataset to extract prompt-response pairs."""
    # Read CSV file
    df = pd.read_csv(input_path)

    # Initialize lists to store prompt-response pairs
    prompts = []
    responses = []

    for _, row in df.iterrows():
        # Split dialog into turns
        dialog_turns = split_dialog(row['dialog'])

        # Create prompt-response pairs (assuming alternating speakers)
        for i in range(0, len(dialog_turns) - 1, 2):
            prompts.append(dialog_turns[i])
            responses.append(dialog_turns[i + 1])

    # Create new DataFrame with prompt-response pairs
    processed_df = pd.DataFrame({
        'prompt': prompts,
        'response': responses
    })

    return processed_df

if __name__ == "__main__":
    # Specify input and output paths
    input_path = "../data/raw/train.csv"  # Adjust to your CSV file path
    output_path = "../data/translated/preprocessed.json"

    # Preprocess dataset
    df = preprocess_dataset(input_path)

    # Save preprocessed file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_json(output_path, orient="records", indent=2)
    print(f"Preprocessed dataset saved to {output_path}")