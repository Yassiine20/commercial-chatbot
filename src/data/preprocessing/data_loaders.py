from torch.utils.data import DataLoader
from .dataset import LanguageDataset


def create_dataloaders(batch_size=16):
    train_dataset = LanguageDataset('data/processed/train.json')
    val_dataset = LanguageDataset('data/processed/val.json')
    test_dataset = LanguageDataset('data/processed/test.json')
    
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

