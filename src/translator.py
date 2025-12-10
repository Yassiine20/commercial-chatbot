"""
LangChain-based translator for multilingual chatbot
Supports: English, French, Arabic, Tunisian Latin
"""
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()


class GeminiTranslator:
    """Translation using LangChain with Google Gemini"""
    
    LANGUAGE_NAMES = {
        'en': 'English',
        'fr': 'French',
        'ar': 'Arabic',
        'tn_latn': 'Tunisian (Latin script)'
    }
    
    def __init__(self, api_key=None, model="gemini-2.5-flash"):
        """
        Initialize LangChain Gemini translator
        
        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
            model: Gemini model to use (default: gemini-2.5-flash)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Initialize LangChain ChatGoogleGenerativeAI
        self.llm = ChatGoogleGenerativeAI(
            api_key=self.api_key,
            model=model,
            temperature=0.3,
            max_output_tokens=500
        )
        
        # Create translation prompt template
        self.translation_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a professional translator. Translate text from {source_lang} to {target_lang} accurately and naturally. Return only the translation without any additional text or explanations."),
            ("user", "Translate the following text from {source_lang} to {target_lang}.\nOnly return the translation, no explanations or additional text.\n\nText to translate: {text}\n\nTranslation:")
        ])
        
        # Create translation chain
        self.translation_chain = self.translation_prompt | self.llm | StrOutputParser()
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text between languages using LangChain
        
        Args:
            text: Text to translate
            source_lang: Source language code (en, fr, ar, tn_latn)
            target_lang: Target language code (en, fr, ar, tn_latn)
            
        Returns:
            Translated text
        """
        # No translation needed if same language
        if source_lang == target_lang:
            return text
        
        # Get language names
        source_name = self.LANGUAGE_NAMES.get(source_lang, source_lang)
        target_name = self.LANGUAGE_NAMES.get(target_lang, target_lang)
        
        try:
            # Use LangChain chain for translation
            translation = self.translation_chain.invoke({
                "source_lang": source_name,
                "target_lang": target_name,
                "text": text
            })
            
            return translation.strip()
            
        except Exception as e:
            print(f"Translation error: {e}")
            # Fallback: return original text
            return text
    
    def translate_batch(self, texts: list, source_lang: str, target_lang: str) -> list:
        """
        Translate multiple texts using LangChain batch processing
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            List of translated texts
        """
        if source_lang == target_lang:
            return texts
        
        # Get language names
        source_name = self.LANGUAGE_NAMES.get(source_lang, source_lang)
        target_name = self.LANGUAGE_NAMES.get(target_lang, target_lang)
        
        try:
            # Use LangChain batch processing
            inputs = [
                {
                    "source_lang": source_name,
                    "target_lang": target_name,
                    "text": text
                }
                for text in texts
            ]
            
            translations = self.translation_chain.batch(inputs)
            return [t.strip() for t in translations]
            
        except Exception as e:
            print(f"Batch translation error: {e}")
            # Fallback: return original texts
            return texts


def test_translator():
    """Test the translator"""
    print("Testing Gemini Translator...")
    
    translator = GeminiTranslator()
    
    # Test cases
    test_cases = [
        ("I want a black jacket", "en", "fr"),
        ("Je veux une veste noire", "fr", "en"),
        ("na7eb jacket ka7la", "tn_latn", "en"),
        ("أريد سترة سوداء", "ar", "en"),
        ("I'm looking for red shoes", "en", "ar"),
        ("Chemise bleue pour homme", "fr", "en"),
        ("n7eb maryoul abyedh", "tn_latn", "en")
    ]
    
    print("\n" + "="*70)
    for text, src, tgt in test_cases:
        print(f"\nOriginal ({src}): {text}")
        translation = translator.translate(text, src, tgt)
        print(f"Translation ({tgt}): {translation}")
        print("-"*70)


if __name__ == '__main__':
    test_translator()
