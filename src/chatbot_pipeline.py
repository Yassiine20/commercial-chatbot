"""
Chatbot Pipeline with Language Detection and LangChain Translation
Handles multilingual conversations for ASOS product recommendations
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from language_detector import LanguageDetector
from translator import GeminiTranslator
from intent_classifier import IntentClassifier
from product_search import ProductSearch
from response_generator import ResponseGenerator

# Load environment variables
load_dotenv()


class ChatbotPipeline:
    """Main chatbot pipeline"""
    
    def __init__(self):
        self.language_detector = None
        self.translator = None
        self.intent_classifier = None
        self.product_search = None
        self.response_generator = None
        
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
        
        # Translator (LangChain + Gemini)
        self.translator = GeminiTranslator()
        print("✓ LangChain Gemini translator loaded")
        
        # Intent classifier (DistilBERT trained model)
        self.intent_classifier = IntentClassifier.load_from_checkpoint(
            checkpoint_path='experiments/DistelBert/best_model.pt',
            model_name='distilbert-base-uncased',
            device='cpu'
        )
        print("✓ Intent classifier loaded (binary: in_context/out_of_context)")

        # Product search engine
        self.product_search = ProductSearch()
        print("✓ Product search engine initialized")

        # Response generator
        self.response_generator = ResponseGenerator(translator=self.translator)
        print("✓ Response generator initialized")
    
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
            print(f"Original: {user_input}")
            print(f"English: {query_english}")
        else:
            query_english = user_input
            print(f"Already in English, no translation needed")
        
        # Step 2.5: Check if query is in-context (shopping-related)
        print("\n[2.5] Checking intent...")
        intent_result = self.intent_classifier.predict(query_english)
        intent = intent_result['intent']
        intent_confidence = intent_result['confidence']
        
        print(f"    Intent: {intent} (confidence: {intent_confidence:.2f})")
        
        # Reject out-of-context queries
        if intent == 'out_of_context' and intent_confidence > 0.75:
            print("    ⚠️  Out-of-context query detected - rejecting")
            return {
                'status': 'rejected',
                'reason': 'out_of_context',
                'message': 'I can only help with shopping and product recommendations. What product are you looking for?',
                'detected_language': detected_lang,
                'language_confidence': confidence,
                'intent': intent,
                'intent_confidence': intent_confidence,
                'query_english': query_english,
                'original_query': user_input
            }
        
        # Step 3: Product Search
        print("\n[3] Searching for products...")
        products = self.product_search.search(query_english, max_results=5)

        if products:
            print(f"    Found {len(products)} matching products:")
            for i, product in enumerate(products, 1):
                print(f"    {i}. {product['name']} - {product['color']} - £{product['price']}")
        else:
            print("    ⚠️  No products found for this query")

        # Step 4: Generate Response
        print("\n[4] Generating response...")
        response = self.response_generator.generate(
            products=products,
            original_language=detected_lang,
            user_query=query_english
        )
        print(f"    Response: {response}")
        
        result = {
            'status': 'success',
            'detected_language': detected_lang,
            'language_confidence': confidence,
            'intent': intent,
            'intent_confidence': intent_confidence,
            'query_english': query_english,
            'original_query': user_input,
            'products': products,
            'response': response
        }
        
        print(f"\n{'='*60}")
        print(f"Processing complete")
        print(f"{'='*60}\n")
        
        return result


def main():
    """Test the pipeline"""
    print("Initializing Chatbot Pipeline...")
    
    # Create pipeline
    pipeline = ChatbotPipeline()
    
    # Load models
    pipeline.load_models()
    
    print("\n" + "="*60)
    print("CHATBOT READY!")
    print("="*60)
    
    # Test messages (mix of in-context and out-of-context)
    test_messages = [
        "I want a black jacket",              # in-context (English)
        #"Je veux un pull noire",              # in-context (French)
        "What's the weather like?",           # out-of-context (English)
        #"na7eb nechri jacket ka7la",          # in-context (Tunisian)
        #"أريد شراء جاكيت أسود",              # in-context (Arabic)
        "Tell me a joke",                     # out-of-context (English)
        "Show me red dresses",                # in-context (English)
        #"9addech el wa9t?",                   # out-of-context (Tunisian - "what time is it?")
    ]
    
    for msg in test_messages:
        result = pipeline.process_message(msg)
        print(f"\nResult: {result}\n")


if __name__ == '__main__':
    main()
