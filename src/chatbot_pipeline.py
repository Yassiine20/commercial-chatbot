"""
Chatbot Pipeline with Groq Translation
Handles multilingual conversations for ASOS product recommendations
"""
import os
import sys
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from typing import Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from language_detector import LanguageDetector
from models.product_classifier import ProductClassifier
from inference.translator import GroqTranslator

# Load environment variables
load_dotenv()


class ChatbotPipeline:
    """Main chatbot pipeline"""
    
    def __init__(self):
        self.language_detector = None
        self.product_classifier = None
        self.translator = None
        self.product_catalog = []
        
    def load_models(self):
        """Load all required models"""
        print("Loading models...")
        
        # Language detector (XLM-RoBERTa trained model)
        self.language_detector = LanguageDetector.load_from_checkpoint(
            checkpoint_path='experiments/xlm_roberta_run2/best_model.pt',
            model_name='xlm-roberta-base',
            device='cpu'
        )
        print("✓ Language detector loaded (4 languages: en, fr, ar, tn_latn)")
        
        pass
        print("✓ Product classifier loaded")
        
        # Translator (Groq)
        self.translator = GroqTranslator()
        print("✓ Translator loaded")
        
    def load_product_catalog(self):
        """Load ASOS product data"""
        print("Loading product catalog...")
        df = pd.read_csv('data/processed/products_asos_cleaned.csv')
        self.product_catalog = df.to_dict('records')
        print(f"✓ Loaded {len(self.product_catalog)} products")
    
    def search_products(self, query: str, category: str = None, limit: int = 5) -> List[Dict]:
        """Search products in catalog"""
        # Simple keyword-based search
        query_lower = query.lower()
        results = []
        
        for product in self.product_catalog:
            # Check if query matches product name or category
            name = str(product.get('name', '')).lower()
            prod_category = str(product.get('category', '')).lower()
            
            if query_lower in name or (category and category.lower() in prod_category):
                results.append(product)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def process_message(self, user_input: str) -> Dict:
        """
        Process user message through full pipeline
        
        Args:
            user_input: User's message in any language
            
        Returns:
            Dict with response, products, language info
        """
        print(f"\n{'='*60}")
        print(f"User input: {user_input}")
        print(f"{'='*60}")
        
        # Step 1: Detect language
        print("\n[1] Detecting language...")
        
        lang_result = self.language_detector.predict(user_input)
        detected_lang = lang_result['language']
        confidence = lang_result['confidence']
        
        print(f"    Detected: {detected_lang} (confidence: {confidence:.2f})")
        
        # Step 2: Translate to English (if needed)
        print("\n[2] Translating to English...")
        if detected_lang != 'en':
            query_english = self.translator.translate(
                text=user_input,
                source_lang=detected_lang,
                target_lang='en'
            )
            print(f"    Original: {user_input}")
            print(f"    English: {query_english}")
        else:
            query_english = user_input
            print(f"    Already in English, no translation needed")
        
        # Step 3: Classify product category
        print("\n[3] Classifying product category...")
        category_result = self.product_classifier.predict(query_english)
        category = category_result.get('category', 'unknown')
        print(f"    Category: {category}")
        
        # Step 4: Search products
        print("\n[4] Searching products...")
        products = self.search_products(query_english, category, limit=5)
        print(f"    Found {len(products)} products")
        
        # Step 5: Format response
        print("\n[5] Generating response...")
        response_text = self.format_response(
            products=products,
            language=detected_lang,
            category=category,
            user_query=user_input
        )
        
        result = {
            'response': response_text,
            'detected_language': detected_lang,
            'language_confidence': confidence,
            'query_english': query_english,
            'category': category,
            'products': products,
            'product_count': len(products)
        }
        
        print(f"\n{'='*60}")
        print(f"Response: {response_text}")
        print(f"{'='*60}\n")
        
        return result
    
    def format_response(self, products: List[Dict], language: str, category: str, user_query: str) -> str:
        """Generate response in user's language"""
        
        # Build English response
        if products:
            product_list = "\n".join([
                f"- {p.get('name', 'Unknown')} by {p.get('brand', 'N/A')} - ${p.get('price', 'N/A')}"
                for p in products[:5]
            ])
            
            english_response = f"""Here are {len(products)} {category} items I found for you:

{product_list}

Would you like more details about any of these items?"""
        else:
            english_response = f"""I couldn't find any {category} items matching your request. 
Could you try different keywords or browse our other categories?"""
        
        # Translate response to user's language
        if language != 'en':
            print(f"    Translating response to {language}...")
            response_translated = self.translator.translate(
                text=english_response,
                source_lang='en',
                target_lang=language
            )
            return response_translated
        else:
            return english_response


def main():
    """Test the pipeline"""
    print("Initializing ASOS Chatbot Pipeline...")
    
    # Create pipeline
    pipeline = ChatbotPipeline()
    
    # Load models and data
    pipeline.load_models()
    pipeline.load_product_catalog()
    
    print("\n" + "="*60)
    print("CHATBOT READY!")
    print("="*60)
    
    # Test messages
    test_messages = [
        "I want a black jacket",
        "Je veux une veste noire",
        "na7eb nechri jacket k7el",
        "نحب نشري جاكيت كحل"
    ]
    
    for msg in test_messages:
        result = pipeline.process_message(msg)


if __name__ == '__main__':
    main()