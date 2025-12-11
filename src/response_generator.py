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
        num_products: int = 3,
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Generate a response based on search results with conversation context
        
        Args:
            products: List of product dictionaries from search
            original_language: User's original language (en, fr, ar, tn_latn)
            user_query: Original user query
            num_products: Number of products to include in response
            conversation_history: Previous conversation exchanges for context
            
        Returns:
            Response string in user's original language
        """
        # Check conversation history for context
        conversation_history = conversation_history or []
        has_history = len(conversation_history) > 0
        
        # No products found
        if not products:
            if has_history:
                # Contextual response referencing previous search
                last_search = conversation_history[-1].get('query_english', 'your previous search')
                response_en = f"I couldn't find any {user_query.lower()} in our catalog. Would you like to try a different style or color? I previously showed you items for '{last_search}' if you'd like to explore similar options."
            else:
                response_en = f"I couldn't find any {user_query.lower()} in our catalog. Would you like to search for something else?"
        
        # Show top results
        else:
            total_products = len(products)
            top_products = products[:num_products]
            
            # Create engaging intro based on number of products and conversation context
            if has_history:
                # Contextual intro acknowledging previous conversation
                if total_products == 1:
                    intro = "Perfect! I found another option for you:"
                elif total_products <= 3:
                    intro = f"Great! Here are {total_products} more products that might interest you:"
                else:
                    intro = f"Excellent! I found {total_products} new options. Here are the top {num_products}:"
            else:
                # First interaction - standard intro
                if total_products == 1:
                    intro = "Perfect! I found exactly what you're looking for:"
                elif total_products <= 3:
                    intro = f"Great! I found {total_products} products that match your search:"
                else:
                    intro = f"Excellent! I found {total_products} products for you. Here are the top {num_products}:"
            
            product_list = []
            for i, p in enumerate(top_products, 1):
                # Format with numbering for better readability
                product_info = f"{i}. {p['name']}\n   {p['color']} • £{p['price']}"
                product_list.append(product_info)
            
            product_text = "\n\n".join(product_list)
            
            # Add helpful closing message
            if total_products > num_products:
                closing = f"\n\n💡 Tip: Scroll down to see all {total_products} products with images. Click any card to view full details and purchase!"
            else:
                closing = "\n\n✨ Click on any product card below to see images and purchase options!"
            
            response_en = f"{intro}\n\n{product_text}{closing}"
        
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
