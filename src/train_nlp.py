import os
import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

class PhishingNLPDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

def compute_metrics(pred):
    """Calculates F1, Recall, Precision, Accuracy, and ROC-AUC per spec."""
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    
    # Convert raw logits to probabilities to calculate ROC-AUC
    probs = torch.tensor(pred.predictions).softmax(dim=-1)[:, 1].numpy()
    
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary')
    acc = accuracy_score(labels, preds)
    
    try:
        auc = roc_auc_score(labels, probs)
    except ValueError:
        auc = 0.0
        
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall,
        'roc_auc': auc
    }

def train_minilm():
    if not os.path.exists(settings.PHIUSIIL_CSV):
        print(f"[-] PhiUSIIL dataset missing at {settings.PHIUSIIL_CSV}. Please download it.")
        return

    print(f"[*] Loading PhiUSIIL Linguistic Dataset from {settings.PHIUSIIL_CSV}")
    df = pd.read_csv(settings.PHIUSIIL_CSV, low_memory=False)
    
    if 'label' not in df.columns:
        raise ValueError("Missing exact 'label' column in Kaggle PhiUSIIL dataset.")
        
    # --- PRO FIX: BALANCE THE DATASET TO PREVENT CLASS COLLAPSE ---
    print("[*] Balancing dataset to prevent NLP majority-class bias...")
    df_phishing = df[df['label'] == 1]
    df_benign = df[df['label'] == 0]

    # Downsample the majority class to exactly match the minority class
    min_class_size = min(len(df_phishing), len(df_benign))
    df_phishing_balanced = df_phishing.sample(n=min_class_size, random_state=42)
    df_benign_balanced = df_benign.sample(n=min_class_size, random_state=42)

    # Combine and shuffle them
    df_balanced = pd.concat([df_phishing_balanced, df_benign_balanced]).sample(frac=1, random_state=42).reset_index(drop=True)

    # Preprocessing: Lowercase the URLs but heavily preserve delimiters (-, ., /, ?) 
    urls = df_balanced['URL'].astype(str).str.lower().tolist()
    labels = df_balanced['label'].astype(int).tolist()
    # ---------------------------------------------------------------
    
    urls_train, urls_test, y_train, y_test = train_test_split(urls, labels, test_size=0.2, random_state=42)

    # Updated to L12 which is officially supported by Microsoft and provides near-BERT accuracy 
    # while comfortably fitting within 6GB VRAM bounds.
    model_name = "microsoft/MiniLM-L12-H384-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    train_encodings = tokenizer(urls_train, truncation=True, padding=True, max_length=settings.TRANSFORMER_MAX_SEQUENCE_LENGTH)
    test_encodings = tokenizer(urls_test, truncation=True, padding=True, max_length=settings.TRANSFORMER_MAX_SEQUENCE_LENGTH)
    
    train_dataset = PhishingNLPDataset(train_encodings, y_train)
    eval_dataset = PhishingNLPDataset(test_encodings, y_test)
    
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    
    training_args = TrainingArguments(
        output_dir=settings.NLP_CHECKPOINT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=settings.BATCH_SIZE,
        per_device_eval_batch_size=settings.BATCH_SIZE,
        learning_rate=2e-5,
        warmup_steps=500,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        fp16=torch.cuda.is_available(),  # Automatically enables mixed precision if your RTX 3060 is detected
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        compute_metrics=compute_metrics
    )
    
    print("[*] Engaging NLP Transformer Fine-Tuning Process...")
    trainer.train()
    
    os.makedirs(settings.NLP_FINAL_DIR, exist_ok=True)
    os.makedirs(settings.NLP_TOKENIZER_DIR, exist_ok=True)
    
    model.save_pretrained(settings.NLP_FINAL_DIR)
    tokenizer.save_pretrained(settings.NLP_TOKENIZER_DIR)
    
    print(f"[+] Fine-tuned MiniLM extracted to {settings.NLP_FINAL_DIR}")
    print(f"[+] Tokenizer configurations saved to {settings.NLP_TOKENIZER_DIR}")

if __name__ == "__main__":
    train_minilm()