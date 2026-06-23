import os

import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from scipy.io import arff
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset

# Import shared ANN architecture
from app.neural_network import PhishingANN

# Configuration
DATA_PATH = "data/phishing_tabular_data/dataset.arff"
MODEL_SAVE_DIR = "models"
ANN_MODEL_PATH = os.path.join(MODEL_SAVE_DIR, "tabular_ann.pt")

# Hyperparameters
BATCH_SIZE = 64
EPOCHS = 50
LEARNING_RATE = 0.001

# Detect Device (Use RTX 3060 if available)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[*] Using device: {device}")


def load_and_preprocess_data(filepath):
    print(f"[*] Loading dataset from {filepath}...")
    data, meta = arff.loadarff(filepath)
    df = pd.DataFrame(data)

    # Decode byte strings to integers
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.decode('utf-8').astype(int)

    # Map Target Variable 'Result' (1 = Phishing, 0 = Legitimate)
    df['Result'] = df['Result'].map({-1: 1, 1: 0})

    X = df.drop(columns=['Result']).values
    y = df['Result'].values

    return X, y


def train_and_evaluate_ann():
    # 1. Load and Split Data
    X, y = load_and_preprocess_data(DATA_PATH)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # 2. Convert to PyTorch Tensors
    X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)

    X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
    y_test_tensor = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)

    # 3. Create DataLoaders
    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, drop_last=True)

    val_dataset = TensorDataset(X_test_tensor, y_test_tensor)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # 4. Initialize Model, Loss, and Optimizer
    input_dim = X_train.shape[1]
    model = PhishingANN(input_dim).to(device)

    criterion = nn.BCEWithLogitsLoss()  # Combines Sigmoid + Binary Cross Entropy safely
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)

    print("\n[*] Starting ANN Training...")

    # 5. Training Loop
    for epoch in range(EPOCHS):
        model.train()
        epoch_loss = 0

        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)

            # Forward pass
            predictions = model(batch_X)
            loss = criterion(predictions, batch_y)

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        model.eval()
        val_loss = 0
        with torch.no_grad():
            for batch_X, batch_y in val_loader:
                batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                predictions = model(batch_X)
                v_loss = criterion(predictions, batch_y)
                val_loss += v_loss.item()
                
        avg_val_loss = val_loss / len(val_loader)
        scheduler.step(avg_val_loss)

        if (epoch + 1) % 10 == 0:
            print(f"    Epoch [{epoch + 1}/{EPOCHS}], Train Loss: {epoch_loss / len(train_loader):.4f}, Val Loss: {avg_val_loss:.4f}")

    # 6. Evaluation
    print("\n[*] Evaluating ANN on Test Data...")
    model.eval()
    with torch.no_grad():
        X_test_tensor = X_test_tensor.to(device)
        y_test_tensor = y_test_tensor.to(device)

        # Get raw logits and apply sigmoid for probabilities
        raw_outputs = model(X_test_tensor)
        probabilities = torch.sigmoid(raw_outputs)

        # Convert to binary predictions (threshold = 0.5)
        y_pred = (probabilities >= 0.5).float()

        # Move back to CPU for Scikit-Learn metrics
        y_pred_np = y_pred.cpu().numpy()
        y_prob_np = probabilities.cpu().numpy()
        y_test_np = y_test_tensor.cpu().numpy()

        acc = accuracy_score(y_test_np, y_pred_np)
        f1 = f1_score(y_test_np, y_pred_np)
        roc_auc = roc_auc_score(y_test_np, y_prob_np)

    print("-" * 50)
    print("PyTorch ANN Evaluation Metrics:")
    print(f"Accuracy : {acc:.4f}")
    print(f"F1-Score : {f1:.4f}")
    print(f"ROC-AUC  : {roc_auc:.4f}")
    print("-" * 50)

    # 7. Save the Model
    if not os.path.exists(MODEL_SAVE_DIR):
        os.makedirs(MODEL_SAVE_DIR)

    torch.save(model.state_dict(), ANN_MODEL_PATH)
    print(f"[+] ANN Model successfully saved to {ANN_MODEL_PATH}")


if __name__ == "__main__":
    train_and_evaluate_ann()