# 🧠 Arabizi Synthetic Dataset Generator

A pipeline to generate **Lebanese Arabizi** (Arabic in Latin script, e.g., "kifak", "mni7", "shou") from English conversational data using:

✅ GPT-based phonetic & cultural translation  
✅ Regex-based Arabizi phonetic correction  
✅ Rule-based orthographic variation generation

---

## 🚀 Features

- Translate English prompt-response pairs into Lebanese Arabizi using GPT-3.5/4
- Correct common phonetic inconsistencies with regex
- Generate 2–3 orthographic variants per sentence to simulate real-world spelling diversity
- Outputs a clean JSON dataset ready for training NLP models


## 📂 Project Structure

```

arabizi_dataset_generator/
│
├── data/                        
│   ├── raw/                         #  Original and Input English dataset (CSV/JSON)
│   ├── translated/                 # processed datasets / GPT-translated Arabizi files
│   ├── corrected/                  # After regex corrections
│   └── final/                      # Final output with variants
│
├── scripts/                         # Core processing scripts
│   ├── 1_preprocess.py             # Clean and prepare English input
│   ├── 2_translate_gpt.py          # Translate to Arabizi via GPT
│   ├── 3_postprocess_regex.py      # Regex-based correction
│   ├── 4_generate_variants.py      # Orthographic variation generation
│   └── 5_save_output.py            # Save final output to JSON
│
├── utils/                           # Helper functions
│   ├── gpt_api.py                  # GPT calling function
│   ├── regex_rules.py              # Regex correction dictionary
│   ├── variant_rules.py            # Variation generation rules
│   └── io_utils.py                 # File I/O utilities
│
├── config/
│ ├── regex_rules.json # Regex phonetic correction patterns
│ └── variant_rules.json # Orthographic transformation rules
│
├── .env                             # Environment variables (e.g., OpenAI key)
├── .gitignore
├── requirements.txt                 # Python dependencies
├── README.md                        # Project overview and setup
└── main.py                          # Entrypoint script to run full pipeline
````

---

## 🧪 Input Format

```json
[
  {
    "prompt": "How are you?",
    "response": "I'm fine, thanks."
  }
]
````

---

## ✅ Output Format

```json
[
  {
    "prompt_en": "How are you?",
    "response_en": "I'm fine, thanks.",
    "prompt_arabizi": "kifak?",
    "response_arabizi": "mnih, merci",
    "prompt_variants": ["keefak?", "kefak?", "kifak?"],
    "response_variants": ["mnee7, masi", "mnih, merci", "mnih, mercee"]
  }
]
```

---

## 📦 Setup & Usage

1. Clone the repo:

```bash
git clone https://github.com/yourusername/arabizi-synthetic-dataset-generator.git
cd arabizi-synthetic-dataset-generator
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add your English data in `data/input_dataset.json`

4. Run the generator:

```bash
python main.py
```

---

## 🔐 OpenAI API Key

Set your OpenAI API key in `gpt_wrapper.py` or via environment variable:

```bash
export OPENAI_API_KEY="your-key-here"
```

---

## ✍️ Author

**Muhammad Fakhar ul Hasnain**
 |  AI Engineer



