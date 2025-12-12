# ChicBot - Multilingual Fashion E-Commerce Chatbot 🛍️

An intelligent, multilingual conversational AI chatbot for fashion e-commerce, supporting English, French, Arabic, and Tunisian dialect. Built with transformer-based models and powered by Google Gemini for natural language understanding.

## ✨ Features

- **🌍 Multilingual Support**: 4 languages (English, French, Arabic, Tunisian Latin)
- **🧠 Smart Intent Classification**: Two-layer validation with DistilBERT + Gemini
- **🔍 Advanced Product Search**: Context-aware search with material, color, and feature filtering
- **💬 Conversation Context**: Tracks conversation history for follow-up queries
- **🎯 Entity Extraction**: Distinguishes product types, materials, colors, brands, sizes, and features
- **⚡ Real-time Translation**: Seamless translation between languages using Gemini
- **🎨 Modern Web UI**: Clean, responsive chat interface

## 🏗️ Architecture

### Core Components

1. **Language Detection** (XLM-RoBERTa)
   - Detects user language with high accuracy
   - Supports code-switching

2. **Intent Classification** (DistilBERT)
   - Binary classification: in_context (shopping) / out_of_context
   - Fast first-layer validation

3. **Entity Extraction** (Gemini 2.5 Flash)
   - Structured output with Pydantic schemas
   - Extracts: product_type, materials, colors, brand, price, sizes, features
   - Context-aware refinement across conversation turns

4. **Product Search Engine**
   - Semantic scoring with multiple factors
   - Pre-filtering by attributes before scoring
   - Word-boundary matching to prevent false positives
   - Material filtering (denim, leather, cotton, etc.)

5. **Response Generation** (Gemini 2.5 Flash)
   - Natural language responses in user's language
   - Personalized product recommendations

## 📁 Project Structure

```
commercial-chatbot/
├── data/
│   ├── products/
│   │   └── products_asos_enhanced.csv       # 30,501 ASOS products
│   ├── language_detection/                  # Language detection datasets
│   │   ├── raw/                             # Per-language JSON files
│   │   ├── generated/                       # Combined datasets
│   │   └── splits/                          # Train/val/test splits
│   └── intent_classification/               # Intent classification datasets
│       ├── raw/                             # Raw training data
│       └── splits/                          # Train/val/test splits
├── src/
│   ├── chatbot_pipeline.py                  # Main orchestration pipeline
│   ├── language_detector.py                 # XLM-RoBERTa language detection
│   ├── intent_classifier.py                 # DistilBERT intent classification
│   ├── entity_extractor.py                  # Gemini entity extraction
│   ├── product_search.py                    # Product search engine
│   ├── translator.py                        # Gemini translation
│   ├── response_generator.py                # Gemini response generation
│   ├── models/                              # Model implementations
│   ├── preprocessing/                       # Data preprocessing
│   └── training/                            # Training utilities
├── experiments/
│   ├── xlm_roberta_run2/                    # Language detection model
│   │   └── best_model.pt
│   └── DistelBert/                          # Intent classification model
│       └── best_model.pt
├── UI/
│   ├── index.html                           # Web interface
│   ├── styles.css
│   └── script.js
├── app.py                                   # Flask API server
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API key ([Get one here](https://ai.google.dev/))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Yassiine20/commercial-chatbot.git
cd commercial-chatbot
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

5. **Run the application**
```bash
python app.py
```

6. **Open in browser**
```
http://localhost:5000
```

## 💡 Usage Examples

### Basic Product Search
```
User: "I want a black dress"
Bot: Shows 5 black dresses with images and prices
```

### Material Refinement
```
User: "is there any trousers?"
Bot: Shows trouser options

User: "jeans"
Bot: Shows denim trousers specifically
```

### Color & Feature Filtering
```
User: "red dresses"
Bot: Shows red dresses

User: "short sleeve"
Bot: Shows red dresses with short sleeves
```

### Multilingual Queries
```
User: "na7eb nechri kabbout k7el"  (Tunisian)
Bot: Translates to "I want to buy a black jacket" and shows results

User: "Je veux une robe rouge"  (French)
Bot: Shows red dresses

User: "أريد جاكيت أسود"  (Arabic)
Bot: Shows black jackets
```

## 🎯 Key Features Explained

### 1. Entity Extraction Schema

The chatbot extracts structured entities from queries:

```python
{
  "product_type": "dress",           # dress, jacket, trousers, etc.
  "materials": ["denim", "leather"], # fabric/material types
  "colors": ["black", "red"],        # color attributes
  "brand": "Nike",                   # brand name
  "price_min": 20.0,                 # minimum price
  "price_max": 50.0,                 # maximum price
  "sizes": ["M", "L"],               # size specifications
  "features": ["short sleeve"],      # style features
  "sort_by": "price_asc",            # sorting preference
  "is_fashion_query": true           # validation flag
}
```

### 2. Context-Aware Refinement

The chatbot remembers conversation context:

```
User: "trousers"
Entities: {product_type: "trousers"}

User: "black"
Entities: {product_type: "trousers", colors: ["black"]}  # Inherits context

User: "jeans"
Entities: {product_type: "trousers", materials: ["denim"], colors: ["black"]}
```

### 3. Two-Layer Validation

Prevents non-fashion queries from reaching the search engine:

1. **Layer 1 (DistilBERT)**: Fast rejection of obvious non-fashion queries
2. **Layer 2 (Gemini)**: Validates ambiguous cases

```
Query: "What's the weather?"
DistilBERT: out_of_context → REJECTED

Query: "bread"
DistilBERT: in_context (0.75)
Gemini: is_fashion_query = False → REJECTED

Query: "black dress"
DistilBERT: in_context (0.99)
Gemini: is_fashion_query = True → PROCEED
```

## 🛠️ Configuration

### Environment Variables

```bash
GEMINI_API_KEY=your_api_key_here
```

### Model Checkpoints

Place trained model checkpoints in:
- `experiments/xlm_roberta_run2/best_model.pt` - Language detection
- `experiments/DistelBert/best_model.pt` - Intent classification

## 📊 Dataset

### ASOS Product Catalog

- **Size**: 30,501 products
- **Fields**: name, category, color, price, SKU, description, images, brand, sizes, materials
- **Categories**: Dresses, jackets, trousers, shoes, accessories, etc.

### Training Data

1. **Language Detection**: 20,475 samples across 4 languages
2. **Intent Classification**: Binary classification (in_context/out_of_context)

## 🧪 Testing

Run the chatbot in test mode:

```bash
python src/chatbot_pipeline.py
```

Test with sample queries:
- "I want a black jacket"
- "Je veux un pull noir"
- "na7eb nechri jacket ka7la"
- "أريد شراء جاكيت أسود"

## 🎨 Web Interface

The UI provides:
- Clean chat interface with message bubbles
- Product cards with images and prices
- "View Product" buttons linking to ASOS
- Conversation history
- Language auto-detection indicator

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **ASOS** for product data
- **Google Gemini** for LLM capabilities
- **Hugging Face** for transformer models
- **XLM-RoBERTa** for multilingual understanding
- **DistilBERT** for efficient intent classification

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for multilingual fashion e-commerce**
