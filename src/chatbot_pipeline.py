"""
Chatbot Pipeline with Language Detection and Translation
Handles multilingual conversations for ASOS product recommendations

TODO: Implement product classification
TODO: Implement product search
TODO: Implement response generation
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from language_detector import LanguageDetector
from translator import GroqTranslator

# Load environment variables
load_dotenv()


class ChatbotPipeline:
    """Main chatbot pipeline"""
    
    def __init__(self):
        self.language_detector = None
        self.translator = None
        
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
        
        # Translator (Groq)
        self.translator = GroqTranslator()
        print("✓ Translator loaded")
    
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
        
        # TODO: Step 3 - Product Classification
        # TODO: Step 4 - Product Search  
        # TODO: Step 5 - Response Generation
        
        result = {
            'detected_language': detected_lang,
            'language_confidence': confidence,
            'query_english': query_english,
            'original_query': user_input
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
    
    # Test messages
    test_messages = [
        "I want a black jacket",
        "Je veux une veste noire",
        "na7eb nechri jacket k7el",
        "نحب نشري جاكيت كحل"
    ]
    
    for msg in test_messages:
        result = pipeline.process_message(msg)
        print(f"\nResult: {result}\n")


if __name__ == '__main__':
    main()
