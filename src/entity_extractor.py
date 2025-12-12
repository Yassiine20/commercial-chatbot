"""Entity extractor using Gemini structured output."""
import os
from typing import Dict, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Define the schema for structured extraction
class ProductEntities(BaseModel):
    """Extracted product entities from user query."""
    
    product_type: Optional[str] = Field(
        description="The type of product being requested (e.g., 'dress', 'jeans', 'jacket'). Normalized to singular."
    )
    colors: List[str] = Field(
        default=[],
        description="List of colors mentioned (e.g., ['blue', 'navy']). Normalized to lowercase."
    )
    price_min: Optional[float] = Field(
        description="Minimum price budget if specified."
    )
    price_max: Optional[float] = Field(
        description="Maximum price budget if specified."
    )
    sizes: List[str] = Field(
        default=[],
        description="Sizes requested (e.g., ['M', 'L', '42'])."
    )
    gender: Optional[str] = Field(
        description="Target gender if specified (e.g., 'women', 'men')."
    )
    brand: Optional[str] = Field(
        description="Brand name if specified (e.g., 'Nike', 'Adidas')."
    )
    features: List[str] = Field(
        default=[],
        description="Style/feature constraints like 'short sleeve', 'long sleeve', 'sleeveless', 'v neck', 'midi', 'mini', 'maxi', 'slim fit', 'oversized'. Lowercase phrases."
    )
    sort_by: Optional[str] = Field(
        description="Sorting preference: 'price_asc', 'price_desc', 'newest'."
    )

class GeminiEntityExtractor:
    def __init__(self, api_key: str = None):
        """Initialize with Gemini API key."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("⚠️ GeminiEntityExtractor: No API Key found.")
        
        # Initialize Gemini Pro
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=0.0
        )
        
        try:
             self.runnable = self.llm.with_structured_output(ProductEntities)
        except Exception as e:
            print(f"⚠️ Structured output initialization failed: {e}. Defaulting to standard generation.")
            self.runnable = None
            
    def extract(self, query: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Extract entities from query, considering history context.
        
        Args:
            query: Current user query
            conversation_history: List of past exchanges for context
            
        Returns:
            Dict matching ProductEntities schema
        """
        if not self.runnable:
            return {}

        # Construct context string
        context_str = ""
        if conversation_history:
            last_exchanges = conversation_history[-3:] # Last 3 turns
            context_str = "\nConversation History:\n"
            for turn in last_exchanges:
                context_str += f"User: {turn.get('user', '')}\nBot: {turn.get('response', '')}\n"

        prompt = f"""
        You are an expert e-commerce shopping assistant.
        Extract structured product attributes from the latest user query.
        Capture style constraints such as sleeve length (short sleeve, long sleeve, sleeveless), dress length (mini, midi, maxi), neckline (v neck), and fit (slim, oversized) inside `features` as lowercase phrases.
        
        {context_str}
        
        Current User Query: "{query}"
        
        Extract the attributes into the defined JSON structure.
        If the user is waiting for a response to a previous question, or acknowledging, exact attributes might be empty.
        If the user adds constraints (e.g. "make it blue"), merge with context implicitly.
        """
        
        try:
            result: ProductEntities = self.runnable.invoke(prompt)
            return result.dict()
        except Exception as e:
            print(f"❌ Entity extraction failed: {e}")
            return {}

# Quick test
if __name__ == "__main__":
    extractor = GeminiEntityExtractor()
    print(extractor.extract("I want a cheap red dress for a wedding"))
