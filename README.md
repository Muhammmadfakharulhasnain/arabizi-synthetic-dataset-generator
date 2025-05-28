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

arabizi-synthetic-dataset-generator/
│
├── main.py                     # Run the full pipeline
├── data/
│   ├── input\_dataset.json      # English prompt-response pairs
│   └── output\_dataset.json     # Final output with Arabizi and variants
│
├── src/
│   ├── utils.py                # File I/O helpers
│   ├── gpt\_wrapper.py          # OpenAI GPT interface
│   ├── transliteration.py      # Regex correction rules
│   ├── orthographic\_variants.py # Rule-based variant generation
│
├── config/
│   ├── regex\_rules.json        # Regex phonetic correction patterns
│   └── variant\_rules.json      # Orthographic transformation rules
│
└── requirements.txt            # Python dependencies

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
Computer Science student |  AI Engineer


```

---

Would you like me to generate this as actual files for download? Or help you write your initial GitHub commit message?
```
