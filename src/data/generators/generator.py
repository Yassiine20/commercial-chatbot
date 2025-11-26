
import random
from typing import List, Dict, Any
from datetime import datetime
import json

from .vocabulary import VOCABULARY, get_random_item
from .templates import TEMPLATES, get_template
from .code_switching import (
    generate_code_switched_sample,
    get_code_switching_distribution,
    CODE_SWITCHING_PATTERNS
)


class Sample:
    
    def __init__(
        self,
        id: str,
        text: str,
        language: str,
        length_category: str,
        has_code_switching: bool = False,
        code_switching_pattern: str = None,
        template_id: str = None
    ):
        self.id = id
        self.text = text
        self.language = language
        self.length_category = length_category
        self.char_count = len(text)
        self.has_code_switching = has_code_switching
        self.code_switching_pattern = code_switching_pattern
        self.template_id = template_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'text': self.text,
            'language': self.language,
            'length_category': self.length_category,
            'char_count': self.char_count,
            'has_code_switching': self.has_code_switching,
            'code_switching_pattern': self.code_switching_pattern,
            'template_id': self.template_id,
        }


class DatasetGenerator:
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)
        
        self.languages = ['en', 'fr', 'ar', 'tn_latn', 'tn_arab']
        self.samples_per_language = 3500
        self.total_samples = len(self.languages) * self.samples_per_language
        
        self.length_distribution = {
            'short': 0.30,
            'medium': 0.50,
            'long': 0.20
        }
        
        self.code_switching_ratio = 0.17
    
    def _fill_template(self, template: str, language: str) -> str:
        text = template
        
        if '{item}' in text:
            text = text.replace('{item}', get_random_item('items', language, self.rng), 1)
        
        if '{color}' in text:
            text = text.replace('{color}', get_random_item('colors', language, self.rng), 1)
        
        if '{size}' in text:
            text = text.replace('{size}', get_random_item('sizes', language, self.rng), 1)
        
        if '{location}' in text:
            text = text.replace('{location}', get_random_item('locations', language, self.rng), 1)
        
        if '{greeting}' in text:
            text = text.replace('{greeting}', get_random_item('greetings', language, self.rng), 1)
        
        if '{price_term}' in text:
            text = text.replace('{price_term}', get_random_item('price_terms', language, self.rng), 1)
        
        if '{availability_term}' in text:
            text = text.replace('{availability_term}', get_random_item('availability_terms', language, self.rng), 1)
        
        return text
    
    def _generate_regular_sample(self, language: str, length_category: str, sample_id: str) -> Sample:
        template = get_template(language, length_category, self.rng)
        template_id = f"{language}_{length_category}_{self.rng.randint(1000, 9999)}"
        text = self._fill_template(template, language)
        
        return Sample(
            id=sample_id,
            text=text,
            language=language,
            length_category=length_category,
            has_code_switching=False,
            template_id=template_id
        )
    
    def _generate_code_switched_sample(self, pattern_key: str, sample_id: str) -> Sample:
        text, target_language = generate_code_switched_sample(pattern_key, VOCABULARY, self.rng)
        
        char_count = len(text)
        if char_count < 50:
            length_category = 'short'
        elif char_count < 150:
            length_category = 'medium'
        else:
            length_category = 'long'
        
        return Sample(
            id=sample_id,
            text=text,
            language=target_language,
            length_category=length_category,
            has_code_switching=True,
            code_switching_pattern=pattern_key,
            template_id=f"cs_{pattern_key}"
        )
    
    def generate_language(self, language: str, count: int) -> List[Sample]:
        samples = []
        
        target_counts = {
            'short': int(count * self.length_distribution['short']),
            'medium': int(count * self.length_distribution['medium']),
            'long': int(count * self.length_distribution['long'])
        }
        
        total_allocated = sum(target_counts.values())
        if total_allocated < count:
            target_counts['medium'] += (count - total_allocated)
        
        sample_idx = 0
        for length_category, target_count in target_counts.items():
            for _ in range(target_count):
                sample_id = f"{language}_{sample_idx:04d}"
                sample = self._generate_regular_sample(language, length_category, sample_id)
                samples.append(sample)
                sample_idx += 1
        
        return samples
    
    def generate_code_switched_samples(self, count: int) -> List[Sample]:
        samples = []
        cs_distribution = get_code_switching_distribution()
        
        pattern_counts = {}
        for pattern, weight in cs_distribution.items():
            pattern_counts[pattern] = int(count * weight)
        
        total_allocated = sum(pattern_counts.values())
        if total_allocated < count:
            pattern_counts['tn_latn_en'] += (count - total_allocated)
        
        sample_idx = 0
        for pattern, pattern_count in pattern_counts.items():
            for _ in range(pattern_count):
                sample_id = f"cs_{sample_idx:04d}"
                sample = self._generate_code_switched_sample(pattern, sample_id)
                samples.append(sample)
                sample_idx += 1
        
        return samples
    
    def generate_all(self) -> List[Sample]:
        all_samples = []
        
        print(f"Generating dataset with seed {self.seed}...")
        print(f"Target: {self.total_samples} samples ({self.samples_per_language} per language)")
        print()
        
        for language in self.languages:
            print(f"Generating {language} samples...")
            samples = self.generate_language(language, self.samples_per_language)
            all_samples.extend(samples)
            print(f"  ✓ Generated {len(samples)} {language} samples")
        
        print()
        
        cs_count = int(self.total_samples * self.code_switching_ratio)
        print(f"Generating {cs_count} code-switched samples...")
        cs_samples = self.generate_code_switched_samples(cs_count)
        all_samples.extend(cs_samples)
        print(f"  ✓ Generated {len(cs_samples)} code-switched samples")
        
        print()
        print(f"Total samples generated: {len(all_samples)}")
        
        self.rng.shuffle(all_samples)
        return all_samples
    
    def export_to_json(self, samples: List[Sample], output_path: str, pretty: bool = True):
        data = {
            'samples': [s.to_dict() for s in samples],
            'metadata': {
                'total_samples': len(samples),
                'generation_date': datetime.now().isoformat(),
                'seed': self.seed,
                'version': '1.0'
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                json.dump(data, f, ensure_ascii=False)
        
        print(f"✓ Exported to {output_path}")
    
    def export_by_language(self, samples: List[Sample], output_dir: str):
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        by_language = {}
        for sample in samples:
            if sample.language not in by_language:
                by_language[sample.language] = []
            by_language[sample.language].append(sample)
        
        for language, lang_samples in by_language.items():
            output_path = os.path.join(output_dir, f"{language}.json")
            self.export_to_json(lang_samples, output_path)
    

