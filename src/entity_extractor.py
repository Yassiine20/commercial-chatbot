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
        description="The type of product (e.g., 'dress', 'trousers', 'jacket', 'coat', 'shirt', 'skirt'). NOT materials like 'denim', 'leather'. Singular form."
    )
    materials: List[str] = Field(
        default=[],
        description="Material/fabric types (e.g., 'denim', 'leather', 'cotton', 'silk', 'wool', 'suede'). Lowercase."
    )
    colors: List[str] = Field(
        default=[],
        description="Color attributes (e.g., ['black', 'red', 'navy blue']). Lowercase."
    )
    price_min: Optional[float] = Field(
        description="Minimum price budget if specified."
    )
    price_max: Optional[float] = Field(
        description="Maximum price budget if specified."
    )
    sizes: List[str] = Field(
        default=[],
        description="Size specifications (e.g., ['M', 'L', '42'])."
    )
    gender: Optional[str] = Field(
        description="Target gender (e.g., 'women', 'men', 'unisex')."
    )
    brand: Optional[str] = Field(
        description="Brand name (e.g., 'Nike', 'Adidas', 'Tommy Jeans')."
    )
    features: List[str] = Field(
        default=[],
        description="Style/design features: 'short sleeve', 'long sleeve', 'sleeveless', 'v neck', 'midi', 'mini', 'maxi', 'slim fit', 'oversized', 'hooded', 'cropped', 'embroidered'. Lowercase phrases."
    )
    sort_by: Optional[str] = Field(
        description="Sort preference: 'price_asc', 'price_desc', 'newest'."
    )
    is_fashion_query: bool = Field(
        description="True if query is about fashion/clothing shopping, False otherwise (food, electronics, general chat)."
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

        # Construct context string with previous entities
        context_str = ""
        previous_entities = None
        
        if conversation_history:
            last_exchanges = conversation_history[-3:]
            context_str = "\nConversation History:\n"
            for turn in last_exchanges:
                context_str += f"User: {turn.get('user', '')}\n"
                if turn.get('entities'):
                    previous_entities = turn.get('entities')

        prompt = f"""
You are an expert fashion e-commerce assistant. Extract structured product attributes from the user query.

CRITICAL DISTINCTIONS:
1. **Product Types** (what item): dress, trousers, jacket, coat, shirt, skirt, shoes, bag
2. **Materials** (what fabric): denim, leather, cotton, silk, wool, suede, linen
3. **Colors** (what color): black, red, blue, white, navy, pink
4. **Features** (style details): short sleeve, long sleeve, midi, mini, hooded, cropped

EXAMPLES:
- "black denim jacket" → product_type='jacket', materials=['denim'], colors=['black']
- "red leather shoes" → product_type='shoes', materials=['leather'], colors=['red']
- "jeans" → materials=['denim'], product_type=use context or leave None
- "trousers" → product_type='trousers'
- "black" → colors=['black'], inherit product_type/materials from context

CONTEXT HANDLING:
If user says just a material/color/feature, they're refining the previous search:
- Previous: product_type='trousers' → User: "jeans" → product_type='trousers', materials=['denim']
- Previous: product_type='dress' → User: "red" → product_type='dress', colors=['red']
- Previous: product_type='jacket' → User: "leather" → product_type='jacket', materials=['leather']

VALIDATION:
- Set `is_fashion_query=True` ONLY for fashion shopping (clothing, shoes, accessories)
- Set `is_fashion_query=False` for food, electronics, services, personal questions

{context_str}

Current Query: "{query}"

Extract attributes. If user is refining previous search, merge with context appropriately.
        """
        
        try:
            result: ProductEntities = self.runnable.invoke(prompt)
            extracted = result.dict()
            
            # Merge with previous context if current query is refinement
            if previous_entities and conversation_history:
                # If no product_type extracted, inherit from previous
                if not extracted.get('product_type') and previous_entities.get('product_type'):
                    extracted['product_type'] = previous_entities['product_type']
                    
                # Merge materials if both exist
                if previous_entities.get('materials'):
                    prev_materials = set(previous_entities['materials'])
                    curr_materials = set(extracted.get('materials', []))
                    extracted['materials'] = list(prev_materials | curr_materials)
                
                # Merge colors if both exist
                if previous_entities.get('colors'):
                    prev_colors = set(previous_entities['colors'])
                    curr_colors = set(extracted.get('colors', []))
                    extracted['colors'] = list(prev_colors | curr_colors)
            
            return extracted
        except Exception as e:
            print(f"❌ Entity extraction failed: {e}")
            return {}

# Quick test
if __name__ == "__main__":
    extractor = GeminiEntityExtractor()
    print(extractor.extract("I want a cheap red dress for a wedding"))
