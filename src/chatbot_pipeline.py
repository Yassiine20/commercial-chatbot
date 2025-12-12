"""
Chatbot Pipeline with Language Detection and LangChain Translation
Handles multilingual conversations for ASOS product recommendations
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from language_detector import LanguageDetector
from translator import GeminiTranslator
from intent_classifier import IntentClassifier
from product_search import ProductSearch
from response_generator import ResponseGenerator
from entity_extractor import GeminiEntityExtractor

# Load environment variables
load_dotenv()


class ChatbotPipeline:
    """Main chatbot pipeline"""
    
    def __init__(self):
        self.language_detector = None
        self.translator = None
        self.intent_classifier = None
        self.entity_extractor = None
        self.product_search = None
        self.response_generator = None
        self.conversation_history = []
        
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
        try:
            self.translator = GeminiTranslator()
            print("✓ LangChain Gemini translator loaded")
        except ValueError as exc:
            # Translator optional; pipeline still works in English-only mode
            print(f"⚠️  Translator disabled ({exc}); will return original text without translation")
            self.translator = None
        
        # Intent classifier (DistilBERT trained model)
        self.intent_classifier = IntentClassifier.load_from_checkpoint(
            checkpoint_path='experiments/DistelBert/best_model.pt',
            model_name='distilbert-base-uncased',
            device='cpu'
        )
        print("✓ Intent classifier loaded (binary: in_context/out_of_context)")

        # Entity Extractor
        self.entity_extractor = GeminiEntityExtractor()
        print("✓ Entity extractor initialized")

        # Product search engine
        self.product_search = ProductSearch()
        print("✓ Product search engine initialized")

        # Response generator
        self.response_generator = ResponseGenerator(translator=self.translator)
        print("✓ Response generator initialized")
    
    def _detect_language(self, text: str) -> Dict:
        """Detect the language of the provided text."""
        return self.language_detector.predict(text)

    def _translate_to_english(self, text: str, detected_lang: str) -> Dict:
        """Translate text to English when required."""
        if detected_lang == 'en':
            return {'text': text, 'translated': False, 'reason': 'already_english'}
        if self.translator is None:
            return {'text': text, 'translated': False, 'reason': 'translator_disabled'}
        try:
            translated = self.translator.translate(
                text=text,
                source_lang=detected_lang,
                target_lang='en'
            )
            return {'text': translated, 'translated': True}
        except Exception as exc:
            print(f"    ⚠️  Translation failed ({exc}); using original text")
            return {'text': text, 'translated': False, 'reason': 'error', 'error': str(exc)}

    def _classify_intent(self, text: str) -> Dict:
        """Classify whether the query is in shopping context."""
        return self.intent_classifier.predict(text)

    def _enrich_query_with_context(self, query: str, conversation_history: List[Dict]) -> str:
        """Enrich query with conversation context for better understanding"""
        if not conversation_history:
            return query
        
        query_lower = query.lower()
        
        # Get the most recent product context
        last_exchange = conversation_history[-1]
        last_query = last_exchange.get('query_english', '')
        
        # Check if query is a follow-up question (doesn't contain product type)
        product_keywords = ['dress', 'jacket', 'coat', 'shirt', 'top', 'pants', 'jeans', 
                          'skirt', 'sweater', 'shoes', 'bag', 'boots', 'sneakers', 'hoodie',
                          'blazer', 'cardigan', 'shorts', 'trousers']
        has_product_keyword = any(keyword in query_lower for keyword in product_keywords)
        
        # Color-only queries (e.g., "what about blue", "show me red ones")
        color_keywords = ['black', 'white', 'red', 'blue', 'green', 'yellow', 'pink', 
                         'purple', 'brown', 'grey', 'gray', 'orange', 'beige', 'navy']
        is_color_change = any(color in query_lower for color in color_keywords) and not has_product_keyword
        
        # Attribute additions (e.g., "long sleeve", "maxi", "mini", "midi")
        attribute_keywords = ['long sleeve', 'short sleeve', 'sleeve', 'maxi', 'midi', 'mini', 
                            'long', 'short', 'casual', 'formal', 'vintage', 'oversized']
        is_attribute_addition = any(attr in query_lower for attr in attribute_keywords) and not has_product_keyword
        
        # Price/modifier queries (e.g., "cheaper ones", "more expensive") - CHECK FIRST
        price_modifiers = ['cheap', 'expensive', 'affordable', 'budget', 'premium', 'lower price', 'higher price']
        is_price_query = any(modifier in query_lower for modifier in price_modifiers) and not has_product_keyword
        
        # Vague follow-ups (e.g., "show me more", "anything else", "other options")
        # But NOT if it's a price query or attribute addition
        vague_followups = ['more', 'other', 'another', 'different', 'else', 'similar', 'like']
        is_vague_followup = any(word in query_lower for word in vague_followups) and not has_product_keyword and not is_price_query and not is_attribute_addition
        
        # Extract product type from last query
        product_type_from_history = None
        for keyword in product_keywords:
            if keyword in last_query.lower():
                product_type_from_history = keyword
                break
        
        # Enrich based on query type
        if is_color_change and product_type_from_history:
            # Replace color in last query with new color
            enriched_query = f"{query_lower} {product_type_from_history}"
            print(f"    💡 Query enriched (color change): '{query}' → '{enriched_query}'")
            return enriched_query
            
        elif is_attribute_addition and product_type_from_history:
            # Extract color from last query if present
            last_color = None
            for color in color_keywords:
                if color in last_query.lower():
                    last_color = color
                    break
            
            # Add attribute to existing product type and color
            if last_color:
                enriched_query = f"{last_color} {product_type_from_history} {query_lower}"
            else:
                enriched_query = f"{product_type_from_history} {query_lower}"
            print(f"    💡 Query enriched (attribute addition): '{query}' → '{enriched_query}'")
            return enriched_query
            
        elif is_price_query and product_type_from_history:
            # Extract color from last query if present
            last_color = None
            for color in color_keywords:
                if color in last_query.lower():
                    last_color = color
                    break
            
            # Keep product type, color, and add price modifier
            if last_color:
                enriched_query = f"{last_color} {product_type_from_history} {query_lower}"
            else:
                enriched_query = f"{product_type_from_history} {query_lower}"
            print(f"    💡 Query enriched (price filter): '{query}' → '{enriched_query}'")
            return enriched_query
            
        elif is_vague_followup and last_query:
            # Use the original query context
            enriched_query = last_query
            print(f"    💡 Query enriched (vague followup): '{query}' → '{enriched_query}'")
            return enriched_query
            
        elif not has_product_keyword and product_type_from_history:
            # Generic follow-up, add product type
            enriched_query = f"{product_type_from_history} {query}"
            print(f"    💡 Query enriched (generic): '{query}' → '{enriched_query}'")
            return enriched_query
        
        return query

    def _extract_entities(self, query: str) -> Dict:
        """Extract structured entities from query using Gemini."""
        if not self.entity_extractor:
            return {}
        return self.entity_extractor.extract(query, self.conversation_history)

    def _search_products(self, query: str, max_results: int = 5, filters: Dict = None, sort_by: str = "relevance") -> List[Dict]:
        """Search catalog for products matching the query."""
        return self.product_search.search(query, max_results=max_results, filters=filters, sort_by=sort_by)

    def _generate_response(self, products: List[Dict], language: str, query_english: str, conversation_history: List[Dict] = None) -> str:
        """Generate a natural-language reply based on search results."""
        return self.response_generator.generate(
            products=products,
            original_language=language,
            user_query=query_english,
            conversation_history=conversation_history
        )

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
        
        lang_result = self._detect_language(user_input)
        detected_lang = lang_result['language']
        confidence = lang_result['confidence']
        
        print(f"    Detected: {detected_lang} (confidence: {confidence:.2f})")
        
        # Step 2: Translate to English (if needed)
        print("\n[2] Translating to English...")
        translation = self._translate_to_english(user_input, detected_lang)
        query_english = translation['text']
        if translation['translated']:
            print(f"Original: {user_input}")
            print(f"English: {query_english}")
        else:
            reason = translation.get('reason')
            if reason == 'already_english':
                print("Already in English, no translation needed")
            elif reason == 'translator_disabled':
                print("⚠️  Translator unavailable; using original text")
            elif reason == 'error':
                print(f"⚠️  Translation failed; using original text")
            else:
                print("No translation applied")
        
        # Step 2.5: Check if query is in-context (shopping-related)
        print("\n[2.5] Checking intent...")
        
        # Always use intent classifier to maintain quality
        intent_result = self._classify_intent(query_english)
        intent = intent_result['intent']
        intent_confidence = intent_result['confidence']
        
        print(f"    DistilBERT Intent: {intent} (confidence: {intent_confidence:.2f})")
        
        # If DistilBERT rejects, reject immediately (no need for Gemini)
        if intent == 'out_of_context':
            print("    ⚠️  Out-of-context query detected - rejecting")
            return {
                'status': 'rejected',
                'reason': 'out_of_context',
                'message': 'I can help with fashion products. What item are you looking for?',
                'detected_language': detected_lang,
                'language_confidence': confidence,
                'intent': intent,
                'intent_confidence': intent_confidence,
                'query_english': query_english,
                'original_query': user_input
            }
        
        # Step 2.75: DistilBERT said in_context, now validate with Gemini
        print("\n[2.75] Extracting entities and validating context with Gemini...")
        
        # Try Gemini entity extraction (if available)
        entities = self._extract_entities(query_english) if self.entity_extractor else {}
        
        # Gemini double-check: both DistilBERT and Gemini must agree it's fashion
        if entities and entities.get('is_fashion_query') is False:
            print("    ⚠️  DistilBERT said in_context, but Gemini says NOT fashion - rejecting")
            return {
                'status': 'rejected',
                'reason': 'not_fashion',
                'message': 'I can help with fashion products. What item are you looking for?',
                'detected_language': detected_lang,
                'language_confidence': confidence,
                'intent': 'out_of_context',
                'intent_confidence': intent_confidence,
                'query_english': query_english,
                'original_query': user_input
            }
        
        if entities and entities.get('is_fashion_query') is True:
            print(f"    ✓ Gemini confirmed: fashion query")
        
        if entities and (entities.get('product_type') or entities.get('colors') or entities.get('features') or entities.get('materials')):
            # Gemini successfully extracted entities - use them
            parts = []
            if entities.get('colors'):
                parts.extend(entities['colors'])
            if entities.get('materials'):
                parts.extend(entities['materials'])
            if entities.get('product_type'):
                parts.append(entities['product_type'])
            if entities.get('brand'):
                parts.append(entities['brand'])
            
            search_query = " ".join(parts)
            print(f"    ✓ Entity-based query (Gemini): '{search_query}'")
            print(f"    📦 Entities: product_type={entities.get('product_type')}, materials={entities.get('materials')}, colors={entities.get('colors')}, brand={entities.get('brand')}, features={entities.get('features')}")
            
        else:
            # Use rule-based enrichment (reliable fallback)
            search_query = self._enrich_query_with_context(query_english, self.conversation_history)
            if search_query != query_english:
                print(f"    ✓ Rule-based enrichment applied")
        
        # Step 3: Product Search
        print("\n[3] Searching for products...")
        filters = {
            'product_type': entities.get('product_type') if entities else None,
            'colors': entities.get('colors') if entities else None,
            'materials': entities.get('materials') if entities else None,
            'brand': entities.get('brand') if entities else None,
            'price_min': entities.get('price_min') if entities else None,
            'price_max': entities.get('price_max') if entities else None,
            'sizes': entities.get('sizes') if entities else None,
            'features': entities.get('features') if entities else None,
        }
        sort_by = entities.get('sort_by') if entities and entities.get('sort_by') else "relevance"

        products = self._search_products(search_query, max_results=5, filters=filters, sort_by=sort_by)

        if products:
            print(f"    Found {len(products)} matching products:")
            for i, product in enumerate(products, 1):
                print(f"    {i}. {product['name']} - {product['color']} - £{product['price']}")
        else:
            print("    ⚠️  No products found for this query")

        # Step 4: Generate Response
        print("\n[4] Generating response...")
        response = self._generate_response(products, detected_lang, query_english, self.conversation_history)
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
        
        # Add to conversation history (store enriched query + entities for better context)
        self.conversation_history.append({
            'user': user_input,
            'query_english': search_query,  # Store enriched query, not original
            'entities': entities,  # Store extracted entities for context merging
            'response': response,
            'products': [p['name'] for p in products[:3]] if products else [],
            'language': detected_lang
        })
        
        # Keep only last 5 exchanges to prevent context overflow
        if len(self.conversation_history) > 5:
            self.conversation_history = self.conversation_history[-5:]
        
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
        "Je veux un pull noire",              # in-context (French)
        "What's the weather like?",           # out-of-context (English)
        "na7eb nechri jacket ka7la",          # in-context (Tunisian)
        "أريد شراء جاكيت أسود",                 # in-context (Arabic)
        "Tell me a joke",                     # out-of-context (English)
        "Show me red dresses",                # in-context (English)
        "9addech el wa9t?",                   # out-of-context (Tunisian - "what time is it?")
    ]
    
    for msg in test_messages:
        result = pipeline.process_message(msg)
        print(f"\nResult: {result}\n")


if __name__ == '__main__':
    main()
