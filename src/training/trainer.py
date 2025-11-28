import torch
import os
from tqdm import tqdm


class Trainer:
    def __init__(self, model, train_loader, val_loader, optimizer, device, save_dir, gradient_accumulation_steps=1, use_fp16=False):
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.optimizer = optimizer
        self.device = device
        self.save_dir = save_dir
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.use_fp16 = use_fp16
        self.scaler = torch.amp.GradScaler('cuda') if use_fp16 else None
        os.makedirs(save_dir, exist_ok=True)
        
    def train_epoch(self):
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        self.optimizer.zero_grad()
        
        for batch_idx, batch in enumerate(tqdm(self.train_loader, desc="Training")):
            input_ids = batch['input_ids'].to(self.device)
            mask = batch['attention_mask'].to(self.device)
            labels = batch['label'].to(self.device)
            
            if self.use_fp16:
                with torch.amp.autocast('cuda'):
                    outputs = self.model(input_ids, mask, labels=labels)
                    loss = outputs.loss / self.gradient_accumulation_steps
                
                self.scaler.scale(loss).backward()
                
                if (batch_idx + 1) % self.gradient_accumulation_steps == 0:
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                    self.optimizer.zero_grad()
                    if self.device.type == 'cuda':
                        torch.cuda.empty_cache()  # Clear cache after optimizer step
            else:
                outputs = self.model(input_ids, mask, labels=labels)
                loss = outputs.loss / self.gradient_accumulation_steps
                
                loss.backward()
                
                if (batch_idx + 1) % self.gradient_accumulation_steps == 0:
                    self.optimizer.step()
                    self.optimizer.zero_grad()
                    if self.device.type == 'cuda':
                        torch.cuda.empty_cache()  # Clear cache after optimizer step
            
            total_loss += outputs.loss.item()
            preds = torch.argmax(outputs.logits, dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
            
            # Clear intermediate tensors
            del input_ids, mask, labels, outputs, loss
        
        # Step optimizer if there are remaining gradients
        if (batch_idx + 1) % self.gradient_accumulation_steps != 0:
            if self.use_fp16:
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                self.optimizer.step()
            self.optimizer.zero_grad()
        
        if self.device.type == 'cuda':
            torch.cuda.empty_cache()
        return total_loss / len(self.train_loader), correct / total

    def evaluate(self):
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch in tqdm(self.val_loader, desc="Validating"):
                input_ids = batch['input_ids'].to(self.device)
                mask = batch['attention_mask'].to(self.device)
                labels = batch['label'].to(self.device)
                
                if self.use_fp16:
                    with torch.amp.autocast('cuda'):
                        outputs = self.model(input_ids, mask, labels=labels)
                else:
                    outputs = self.model(input_ids, mask, labels=labels)
                    
                total_loss += outputs.loss.item()
                
                preds = torch.argmax(outputs.logits, dim=1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)
                
        return total_loss / len(self.val_loader), correct / total

    def train(self, epochs):
        best_acc = 0
        
        for epoch in range(epochs):
            print(f"\nEpoch {epoch+1}/{epochs}")
            
            train_loss, train_acc = self.train_epoch()
            val_loss, val_acc = self.evaluate()
            
            print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc*100:.2f}%")
            print(f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc*100:.2f}%")
            
            if val_acc > best_acc:
                best_acc = val_acc
                torch.save(self.model.state_dict(), os.path.join(self.save_dir, 'best_model.pt'))
                print(f"✓ Saved best model")
        
        print(f"\nBest Accuracy: {best_acc*100:.2f}%")

