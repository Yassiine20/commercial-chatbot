import json
import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer


class LanguageDataset(Dataset):
    def __init__(self, json_path, max_length=128, model_name='xlm-roberta-base'):
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        self.samples = data['samples']
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_length = max_length
        self.label_map = {'en': 0, 'fr': 1, 'ar': 2, 'tn_latn': 3}
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        
        encoding = self.tokenizer(
            sample['text'],
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'label': torch.tensor(self.label_map[sample['language']])
        }

