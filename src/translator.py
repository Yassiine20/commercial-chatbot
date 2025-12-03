"""
Groq-based translator for multilingual chatbot
Supports: English, French, Arabic, Tunisian Latin
"""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class GroqTranslator:
    """Translation using Groq API"""
    
    LANGUAGE_NAMES = {
        'en': 'English',
        'fr': 'French',
        'ar': 'Arabic',
        'tn_latn': 'Tunisian (Latin script)'
    }
    
    def __init__(self, api_key=None, model="llama-3.3-70b-versatile"):
        """
        Initialize Groq translator
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: Groq model to use
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=self.api_key)
        self.model = model
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text between languages
        
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
        
        # Build translation prompt
        prompt = f"""Translate the following text from {source_name} to {target_name}.
                Only return the translation, no explanations or additional text.
                Text to translate: {text}

                Translation:"""
        
        try:
            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator. Translate text from {source_name} to {target_name} accurately and naturally. Return only the translation without any additional text or explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.3,  # Low temperature for consistent translations
                max_tokens=500
            )
            
            translation = chat_completion.choices[0].message.content.strip()
            return translation
            
        except Exception as e:
            print(f"Translation error: {e}")
            # Fallback: return original text
            return text
    
    def translate_batch(self, texts: list, source_lang: str, target_lang: str) -> list:
        """
        Translate multiple texts
        
        Args:
            texts: List of texts to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            List of translated texts
        """
        if source_lang == target_lang:
            return texts
        
        translations = []
        for text in texts:
            translation = self.translate(text, source_lang, target_lang)
            translations.append(translation)
        
        return translations


def test_translator():
    """Test the translator"""
    print("Testing Groq Translator...")
    
    translator = GroqTranslator()
    
    # Test cases
    test_cases = [
        ("I want a black jacket", "en", "fr"),
        ("Je veux une veste noire", "fr", "en"),
        ("na7eb jacket ka7la", "tn_latn", "en"),
        ("أريد سترة سوداء", "ar", "en"),
        ("I'm looking for red shoes", "en", "ar"),
        ("Chemise bleue pour homme", "fr", "en")
    ]
    
    print("\n" + "="*70)
    for text, src, tgt in test_cases:
        print(f"\nOriginal ({src}): {text}")
        translation = translator.translate(text, src, tgt)
        print(f"Translation ({tgt}): {translation}")
        print("-"*70)


if __name__ == '__main__':
    test_translator()
