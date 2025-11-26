from typing import Dict, List, Tuple
import random



CODE_SWITCHING_PATTERNS = {
    'tn_latn_en': {
        'target_language': 'tn_latn', 
        'templates': [
            "salam, I want {item}",
            "n7eb {item} please",
            "available fi {color}?",
            "{greeting}, I need {item} in {size}",
            "b9adech for the {item}?",
            "fama {item} available?",
            "na7eb nechri {item}, do you have in {color}?",
            "I want {item}, b9adech?",
            "{item} fi {color} please",
            "chkoun lena, I need size {size}",
        ],
    },
    'tn_latn_fr': {
        'target_language': 'tn_latn',
        'templates': [
            "salam, je veux {item}",
            "b9adech el {item}?",
            "fama en {color}?",
            "{greeting}, je cherche {item}",
            "na7eb {item} en taille {size}",
            "vous avez {item} fi {color}?",
            "je veux {item}, b9adech?",
            "3andkom le {item} disponible?",
            "{item} en {color} s'il vous plaît",
            "chhal pour le {item}?",
        ],
    },
    'tn_arab_en': {
        'target_language': 'tn_arab',
        'templates': [
            "سلام, I want {item}",
            "نحب {item} please",
            "available في {color}؟",
            "{greeting}, I need {item}",
            "بقداش for the {item}?",
            "فما {item} available?",
            "نحب نشري {item}, do you have?",
            "I want {item}, بقداش؟",
        ],
    },
    'tn_arab_fr': {
        'target_language': 'tn_arab',
        'templates': [
            "سلام, je veux {item}",
            "بقداش le {item}?",
            "فما en {color}?",
            "{greeting}, je cherche {item}",
            "نحب {item} en taille {size}",
            "vous avez {item} في {color}?",
            "عندكم le {item}?",
        ],
    },
    'ar_en': {
        'target_language': 'ar',
        'templates': [
            "مرحبا, I need {item}",
            "هل لديكم {item} available?",
            "I want {item} باللون {color}",
            "{greeting}, do you have {item}?",
            "أريد {item} in size {size}",
            "available في {color}?",
        ],
    },
    'ar_fr': {
        'target_language': 'ar',
        'templates': [
            "مرحبا, je veux {item}",
            "vous avez {item} باللون {color}?",
            "أريد {item} en taille {size}",
            "{greeting}, je cherche {item}",
            "هل لديكم {item} disponible?",
        ],
    },
    'fr_en': {
        'target_language': 'fr',
        'templates': [
            "Bonjour, I want {item}",
            "C'est available en {color}?",
            "Je veux {item} in size {size}",
            "Do you have {item} en {color}?",
            "{greeting}, I need {item}",
        ],
    },
    'en_fr': {
        'target_language': 'en',
        'templates': [
            "Hello, je veux {item}",
            "I want {item} en {color}",
            "Available en taille {size}?",
            "Do you have {item} disponible?",
        ],
    },
}


def generate_code_switched_sample(
    pattern_key: str,
    vocabulary: Dict,
    rng: random.Random
) -> Tuple[str, str]:
    """
    Generate a code-switched sample.
    
    Args:
        pattern_key: Key identifying the code-switching pattern (e.g., 'tn_latn_en')
        vocabulary: Vocabulary dictionary
        rng: Random number generator
        
    Returns:
        Tuple of (generated_text, target_language)
    """
    if pattern_key not in CODE_SWITCHING_PATTERNS:
        raise ValueError(f"Unknown code-switching pattern: {pattern_key}")
    
    pattern = CODE_SWITCHING_PATTERNS[pattern_key]
    template = rng.choice(pattern['templates'])
    target_language = pattern['target_language']
    
   
    text = template
    
    # Replace placeholders
    if '{item}' in text:
        # Use target language vocabulary
        items = vocabulary['items'].get(target_language, vocabulary['items']['en'])
        text = text.replace('{item}', rng.choice(items), 1)
    
    if '{color}' in text:
        colors = vocabulary['colors'].get(target_language, vocabulary['colors']['en'])
        text = text.replace('{color}', rng.choice(colors), 1)
    
    if '{size}' in text:
        text = text.replace('{size}', rng.choice(vocabulary['sizes']['all']), 1)
    
    if '{location}' in text:
        locations = vocabulary['locations'].get(target_language, vocabulary['locations']['en'])
        text = text.replace('{location}', rng.choice(locations), 1)
    
    if '{greeting}' in text:
        greetings = vocabulary['greetings'].get(target_language, vocabulary['greetings']['en'])
        text = text.replace('{greeting}', rng.choice(greetings), 1)
    
    if '{price_term}' in text:
        price_terms = vocabulary['price_terms'].get(target_language, vocabulary['price_terms']['en'])
        text = text.replace('{price_term}', rng.choice(price_terms), 1)
    
    if '{availability_term}' in text:
        avail_terms = vocabulary['availability_terms'].get(target_language, vocabulary['availability_terms']['en'])
        text = text.replace('{availability_term}', rng.choice(avail_terms), 1)
    
    return text, target_language


def get_code_switching_distribution() -> Dict[str, float]:
    """
    Get the distribution of code-switching patterns.
    
    Returns:
        Dictionary mapping pattern keys to their relative weights
    """
    return {
        'tn_latn_en': 0.25,   
        'tn_latn_fr': 0.25,   
        'tn_arab_en': 0.15,   
        'tn_arab_fr': 0.15,   
        'ar_en': 0.08,        
        'ar_fr': 0.07,      
        'fr_en': 0.03,        
        'en_fr': 0.02,        
    }
