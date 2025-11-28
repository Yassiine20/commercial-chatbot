from torch.utils.data import DataLoader
from .dataset import LanguageDataset


def get_dataloaders(batch_size=16, model_name='xlm-roberta-base', max_length=128):
    train_dataset = LanguageDataset('data/language_detection/splits/train.json', max_length=max_length, model_name=model_name)
    val_dataset = LanguageDataset('data/language_detection/splits/val.json', max_length=max_length, model_name=model_name)
    test_dataset = LanguageDataset('data/language_detection/splits/test.json', max_length=max_length, model_name=model_name)
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=32,
        shuffle=False
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=32,
        shuffle=False
    )
    
    return train_loader, val_loader, test_loader

