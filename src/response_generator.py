"""
Response Generator for Chatbot
Formats product results into natural language responses
"""
from typing import Dict, List


class ResponseGenerator:
    """Generate natural language responses from product search results"""
    
    def __init__(self, translator=None):
        """
        Initialize response generator
        
        Args:
            translator: Translator instance for multilingual responses
        """
        self.translator = translator
    
    def generate(
        self,
        products: List[Dict],
        original_language: str,
        user_query: str,
        num_products: int = 3
    ) -> str:
        """
        Generate a response based on search results
        
        Args:
            products: List of product dictionaries from search
            original_language: User's original language (en, fr, ar, tn_latn)
            user_query: Original user query
            num_products: Number of products to include in response
            
        Returns:
            Response string in user's original language
        """
        # No products found
        if not products:
            response_en = f"I couldn't find any {user_query.lower()} in our catalog. Would you like to search for something else?"
        
        # Show top results
        else:
            top_products = products[:num_products]
            product_list = "\n".join([
                f"• {p['name']} ({p['color']}) - £{p['price']}"
                for p in top_products
            ])
            
            response_en = f"Great! I found {len(products)} products matching '{user_query}':\n\n{product_list}\n\nWould you like more details about any of these items?"
        
        # Translate back to original language if needed
        if original_language != 'en' and self.translator:
            try:
                response = self.translator.translate(
                    text=response_en,
                    source_lang='en',
                    target_lang=original_language
                )
                return response
            except Exception as e:
                print(f"Warning: Translation failed ({e}), returning English response")
                return response_en
        
        return response_en
