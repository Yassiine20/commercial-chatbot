# Multilingual Chatbot - Language Detection

XLM-RoBERTa-based language detection for a fashion e-commerce chatbot supporting 5 languages including Tunisian dialect.

## Languages Supported

- **English (en)**: Standard English
- **French (fr)**: Standard French
- **Standard Arabic (ar)**: Modern Standard Arabic
- **Tunisian Latin (tn_latn)**: Tunisian dialect in Latin script (e.g., "na7eb nechri jacket")
- **Tunisian Arabic (tn_arab)**: Tunisian dialect in Arabic script (e.g., "نحب نشري جاكيت")

## Project Structure

```
commercial-chatbot/
├── data/
│   ├── products_asos.csv                    # Original product data
│   ├── products_asos_cleaned.csv           # Cleaned product data
│   ├── raw/                                 # Legacy raw data
│   ├── processed/                           # Legacy processed data
│   └── language_detection/                  # Language detection datasets
│       ├── raw/                             # Per-language JSON files
│       │   ├── en.json
│       │   ├── fr.json
│       │   ├── ar.json
│       │   ├── tn_latn.json
│       │   └── tn_arab.json
│       ├── generated/                       # Combined datasets
│       │   └── combined_dataset.json
│       └── splits/                          # Train/val/test splits
│           ├── train.json                   # 70% (14,332 samples)
│           ├── val.json                     # 15% (3,071 samples)
│           └── test.json                    # 15% (3,072 samples)
├── src/
│   ├── data/
│   │   ├── generators/                      # Dataset generation
│   │   │   ├── generator.py                 # Main generator
│   │   │   ├── templates.py                 # Language templates
│   │   │   ├── vocabulary.py                # Product vocabulary
│   │   │   └── code_switching.py            # Code-switching patterns
│   │   └── preprocessing/                   # Data preprocessing
│   │       ├── split_dataset.py             # Dataset splitting
│   │       ├── dataset.py                   # PyTorch datasets
│   │       └── data_loaders.py              # Data loaders
│   ├── models/                              # Model implementations
│   ├── training/                            # Training utilities
│   ├── evaluation/                          # Evaluation utilities
│   └── utils/                               # General utilities
├── scripts/
│   └── data_generation/
│       └── generate_dataset.py              # Dataset generation script
├── notebooks/
│   ├── 01_data_exploration.ipynb            # Product data EDA
│   ├── 02_data_cleaning.ipynb               # Product data cleaning
│   └── 03_product_classifier_training.ipynb # Keyword-based classifier
├── ui/                                      # Web interface
│   ├── chat.html
│   ├── styles.css
│   └── script.js
├── configs/                                 # Configuration files
├── experiments/                             # Experiment tracking
├── requirements.txt
└── README.md
```

## Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```


## Usage

### Step 1: Generate Dataset

Generate 20,475 synthetic samples across 5 languages:

```bash
python3 scripts/data_generation/generate_dataset.py
```

**Options:**

- `--seed`: Random seed (default: 42)
- `--output-dir`: Output directory (default: data/language_detection/generated)

**Output:**

- `data/language_detection/generated/combined_dataset.json`: All samples combined
- `data/language_detection/raw/<language>.json`: Per-language files

**Dataset Statistics:**

- Total samples: 20,475
- Samples per language: ~3,500 (regular) + code-switched samples
- Code-switching: ~17% of samples
- Length distribution: 30% short, 50% medium, 20% long

### Step 2: Split Dataset

Split the dataset into train/validation/test sets (70/15/15):

```bash
python3 src/data/preprocessing/split_dataset.py
```

**Options:**

- `--input`: Input dataset (default: data/language_detection/generated/combined_dataset.json)
- `--output-dir`: Output directory (default: data/language_detection/splits)
- `--seed`: Random seed (default: 42)

**Output:**

- `data/language_detection/splits/train.json`: 14,332 samples (70%)
- `data/language_detection/splits/val.json`: 3,071 samples (15%)
- `data/language_detection/splits/test.json`: 3,072 samples (15%)

**Stratified Splitting:**
Each split maintains the same language distribution as the original dataset.

## Dataset Details

### Code-Switching

The dataset includes realistic code-switching patterns common in multilingual contexts:

- **Tunisian + English**: "salam, I want jacket"
- **Tunisian + French**: "b9adech le bomber?"
- **Arabic + French**: "مرحبا, je veux veste"

Code-switched samples are labeled by their dominant language.

### Sample Examples

**English:**

```
"I want to buy a black bomber jacket in size L"
"Do you have this jacket in size M?"
```

**French:**

```
"Je veux acheter un manteau noir en taille L"
"Vous avez cette veste en taille M?"
```

**Standard Arabic:**

```
"أريد شراء جاكيت أسود بمقاس L"
"هل لديكم هذا الجاكيت بمقاس M؟"
```

**Tunisian Latin:**

```
"na7eb nechri kabbout k7el taille L"
"3andkom jacket fi taille M?"
```

**Tunisian Arabic:**

```
"نحب نشري كبوط كحل تاي L"
"عندكم جاكيت في تاي M؟"
```

## Next Steps

- [ ] Create PyTorch Dataset class
- [ ] Implement XLM-RoBERTa training script
- [ ] Train the model
- [ ] Evaluate performance
- [ ] Deploy for inference

## Model Architecture

**Base Model:** XLM-RoBERTa-base

- Pre-trained on 100 languages
- Handles multilingual text natively
- Supports mixed scripts (Latin + Arabic)

**Task:** 5-class classification

- Input: User message text
- Output: Language label (en, fr, ar, tn_latn, tn_arab)


