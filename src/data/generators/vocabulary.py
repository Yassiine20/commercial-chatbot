

VOCABULARY = {
    'items': {
        'en': [
            'coat', 'jacket', 'bomber', 'blazer', 'parka', 
            'windbreaker', 'trench coat', 'winter coat', 'leather jacket',
            'denim jacket', 'fleece jacket', 'rain coat', 'overcoat'
        ],
        'fr': [
            'manteau', 'veste', 'bomber', 'blazer', 'parka', 
            'coupe-vent', 'trench', 'manteau d\'hiver', 'veste en cuir',
            'veste en jean', 'veste polaire', 'imperméable', 'pardessus'
        ],
        'ar': [
            'معطف', 'جاكيت', 'بومبر', 'بليزر', 'باركا',
            'جاكيت جلد', 'معطف شتوي', 'جاكيت جينز', 'معطف مطر'
        ],
        'tn_latn': [
            'kabbout', 'veste', 'bomber', 'blazer', 'parka',
            'jacket', 'manteau', 'kabbout dhiver', 'veste jeans'
        ],
        'tn_arab': [
            'كبوط', 'جاكيت', 'بومبر', 'بليزر', 'باركا',
            'فيست', 'مونطو', 'كبوط ديفير', 'فيست جينز'
        ],
    },
    
    'colors': {
        'en': [
            'black', 'grey', 'gray', 'pink', 'purple', 'stone', 
            'ecru', 'neutral', 'beige', 'navy', 'white', 'cream',
            'dark grey', 'light grey', 'charcoal'
        ],
        'fr': [
            'noir', 'gris', 'rose', 'violet', 'pierre', 'écru', 
            'neutre', 'beige', 'marine', 'blanc', 'crème',
            'gris foncé', 'gris clair', 'anthracite'
        ],
        'ar': [
            'أسود', 'رمادي', 'وردي', 'بنفسجي', 'حجري', 'بيج',
            'محايد', 'كحلي', 'أبيض', 'كريمي', 'رمادي غامق'
        ],
        'tn_latn': [
            'k7el', 'gris', 'rose', 'violet', 'beige', 'blanc',
            'noir', 'kre7li', 'gris fonce', 'gris clair'
        ],
        'tn_arab': [
            'كحل', 'رمادي', 'روز', 'بنفسجي', 'بيج', 'أبيض',
            'نوار', 'كريمي', 'رمادي غامق', 'رمادي فاتح'
        ],
    },
    
    'sizes': {
        'all': ['XS', 'S', 'M', 'L', 'XL', 'XXL', '3XL', '2XL']
    },
    
    'locations': {
        'en': ['Tunisia', 'Tunis', 'Sfax', 'Sousse', 'Ariana', 'Bizerte'],
        'fr': ['Tunisie', 'Tunis', 'Sfax', 'Sousse', 'Ariana', 'Bizerte'],
        'ar': ['تونس', 'تونس العاصمة', 'صفاقس', 'سوسة', 'أريانة', 'بنزرت'],
        'tn_latn': ['Tunis', 'Sfax', 'Sousse', 'Ariana', 'Bizerte', 'Nabeul'],
        'tn_arab': ['تونس', 'صفاقس', 'سوسة', 'أريانة', 'بنزرت', 'نابل'],
    },
    
    'price_terms': {
        'en': ['price', 'cost', 'how much', 'total', 'payment'],
        'fr': ['prix', 'coût', 'combien', 'total', 'paiement'],
        'ar': ['السعر', 'الثمن', 'كم', 'المجموع', 'الدفع'],
        'tn_latn': ['b9adech', 'prix', 'combien', 'chhal', 'total'],
        'tn_arab': ['بقداش', 'الثمن', 'شحال', 'السعر', 'توتال'],
    },
    
    'availability_terms': {
        'en': ['available', 'in stock', 'have', 'do you have'],
        'fr': ['disponible', 'en stock', 'avez-vous', 'vous avez'],
        'ar': ['متوفر', 'موجود', 'هل لديكم', 'عندكم'],
        'tn_latn': ['fama', 'disponible', '3andkom', 'mawjoud'],
        'tn_arab': ['فما', 'متوفر', 'عندكم', 'موجود'],
    },
    
    'greetings': {
        'en': ['hello', 'hi', 'hey', 'good morning', 'good evening'],
        'fr': ['bonjour', 'salut', 'bonsoir', 'coucou'],
        'ar': ['مرحبا', 'السلام عليكم', 'أهلا', 'صباح الخير', 'مساء الخير'],
        'tn_latn': ['salam', 'ahla', 'bonjour', 'bonsoir', 'ya7chitek'],
        'tn_arab': ['سلام', 'أهلا', 'بونجور', 'بونسوار', 'يحشيك'],
    }
}


def get_random_item(category: str, language: str, rng) -> str:
    """
    Get a random item from vocabulary.
    
    Args:
        category: Vocabulary category (e.g., 'items', 'colors')
        language: Language code
        rng: Random number generator
        
    Returns:
        Random vocabulary item
    """
    if category == 'sizes':
        return rng.choice(VOCABULARY['sizes']['all'])
    
    if category not in VOCABULARY:
        raise ValueError(f"Unknown category: {category}")
    
    if language not in VOCABULARY[category]:
        raise ValueError(f"Language {language} not found in category {category}")
    
    return rng.choice(VOCABULARY[category][language])
