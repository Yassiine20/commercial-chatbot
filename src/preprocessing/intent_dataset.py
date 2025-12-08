"""
Intent Classification Dataset
For loading in-context vs out-of-context data
"""
import json
import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer


class IntentDataset(Dataset):
    """
    Dataset for intent classification (binary: in_context vs out_of_context)
    
    Args:
        json_path: Path to JSON file with samples
        max_length: Maximum sequence length for tokenization
        model_name: Pre-trained model name for tokenizer
    """
    
    def __init__(self, json_path, max_length=128, model_name='distilbert-base-uncased'):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.samples = data['samples']
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_length = max_length
        
        # Binary classification mapping
        self.label_map = {
            'in_context': 0,
            'out_of_context': 1
        }
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        
        # Tokenize text
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
            'label': torch.tensor(self.label_map[sample['intent']])
        }


def get_intent_dataloaders(batch_size=16, model_name='distilbert-base-uncased', max_length=128):
    """
    Create train, validation, and test dataloaders for intent classification
    
    Args:
        batch_size: Batch size for training
        model_name: Model name for tokenizer
        max_length: Maximum sequence length
        
    Returns:
        train_loader, val_loader, test_loader
    """
    from torch.utils.data import DataLoader
    
    # Create datasets
    train_dataset = IntentDataset(
        'data/intent_classification/splits/train.json',
        max_length=max_length,
        model_name=model_name
    )
    
    val_dataset = IntentDataset(
        'data/intent_classification/splits/val.json',
        max_length=max_length,
        model_name=model_name
    )
    
    test_dataset = IntentDataset(
        'data/intent_classification/splits/test.json',
        max_length=max_length,
        model_name=model_name
    )
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    return train_loader, val_loader, test_loader
