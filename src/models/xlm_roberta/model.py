import torch
import torch.nn as nn
from transformers import AutoModel, BitsAndBytesConfig
from peft import get_peft_model, LoraConfig, TaskType, prepare_model_for_kbit_training


class XLMRobertaClassifier(nn.Module):
    def __init__(self, num_labels=5, model_name='xlm-roberta-base', gradient_checkpointing=False, 
                 load_in_8bit=False, use_lora=False, lora_r=16, lora_alpha=32, lora_dropout=0.05):
        super().__init__()
        
        # Configure 8-bit quantization
        if load_in_8bit:
            bnb_config = BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_threshold=6.0,
                llm_int8_has_fp16_weight=False,
            )
            # Load base model only (without classification head)
            self.roberta = AutoModel.from_pretrained(
                model_name,
                quantization_config=bnb_config,
                device_map="auto"
            )
            
            # Prepare model for k-bit training
            self.roberta = prepare_model_for_kbit_training(self.roberta)
            
            # Add LoRA adapters
            if use_lora:
                peft_config = LoraConfig(
                    task_type=TaskType.FEATURE_EXTRACTION,
                    r=lora_r,
                    lora_alpha=lora_alpha,
                    lora_dropout=lora_dropout,
                    bias="none",
                    target_modules=["query", "value"],
                )
                self.roberta = get_peft_model(self.roberta, peft_config)
                self.roberta.print_trainable_parameters()
            
            # Add custom classifier head (not quantized)
            hidden_size = self.roberta.config.hidden_size
            self.classifier = nn.Sequential(
                nn.Dropout(0.1),
                nn.Linear(hidden_size, num_labels)
            ).cuda()  # Move classifier to GPU
        else:
            self.roberta = AutoModel.from_pretrained(model_name)
            hidden_size = self.roberta.config.hidden_size
            self.classifier = nn.Sequential(
                nn.Dropout(0.1),
                nn.Linear(hidden_size, num_labels)
            )
        
        if gradient_checkpointing and not load_in_8bit:
            self.roberta.gradient_checkpointing_enable()
        
        self.num_labels = num_labels
        self.loss_fn = nn.CrossEntropyLoss()
    
    def forward(self, input_ids, attention_mask, labels=None):
        outputs = self.roberta(input_ids=input_ids, attention_mask=attention_mask)
        # Use CLS token representation
        pooled_output = outputs.last_hidden_state[:, 0, :]
        logits = self.classifier(pooled_output)
        
        loss = None
        if labels is not None:
            loss = self.loss_fn(logits, labels)
        
        # Return in the same format as HuggingFace models
        from types import SimpleNamespace
        return SimpleNamespace(loss=loss, logits=logits)

