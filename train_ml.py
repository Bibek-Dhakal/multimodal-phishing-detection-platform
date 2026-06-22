import os
import pickle

import pandas as pd
from scipy.io import arff
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

# Configuration
DATA_PATH = "data/phishing_tabular_data/dataset.arff"
MODEL_SAVE_DIR = "models"
BEST_MODEL_PATH = os.path.join(MODEL_SAVE_DIR, "best_traditional_ml.pkl")


def load_and_preprocess_data(filepath):
    print(f"[*] Loading dataset from {filepath}...")
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Dataset not found at {filepath}. Please ensure your file is named 'dataset.arff' and placed in the 'data/' folder.")

    # Load ARFF file
    data, meta = arff.loadarff(filepath)
    df = pd.DataFrame(data)

    # ARFF loads nominal attributes as byte strings (e.g., b'-1'). We need to decode and convert them to integers.
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.decode('utf-8').astype(int)

    # Map Target Variable 'Result'
    # Original: -1 (Phishing), 1 (Legitimate)
    # New: 1 (Phishing), 0 (Legitimate) -> This is required for XGBoost and standardizes the metrics.
    print("[*] Mapping target variables...")
    df['Result'] = df['Result'].map({-1: 1, 1: 0})

    X = df.drop(columns=['Result'])
    y = df['Result']

    return X, y


def train_and_evaluate():
    # 1. Load Data
    X, y = load_and_preprocess_data(DATA_PATH)

    # 2. Split Data (80% Training, 20% Testing)
    print("[*] Splitting data into 80% train, 20% test...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # 3. Define Models
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Naive Bayes": GaussianNB(),
        "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=5),
        "Support Vector Machine": SVC(probability=True, random_state=42),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "AdaBoost": AdaBoostClassifier(random_state=42),
        "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    }

    results = []
    best_f1 = 0
    best_model_name = ""
    best_model = None

    print("\n[*] Training and Evaluating 8 Machine Learning Models...")
    print("-" * 65)
    print(f"{'Model Name':<25} | {'Accuracy':<8} | {'F1-Score':<8} | {'ROC-AUC':<8}")
    print("-" * 65)

    # 4. Train & Evaluate each model
    for name, model in models.items():
        # Train
        model.fit(X_train, y_train)

        # Predict
        y_pred = model.predict(X_test)
        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X_test)[:, 1]
            roc_auc = roc_auc_score(y_test, y_proba)
        else:
            roc_auc = roc_auc_score(y_test, y_pred)  # Fallback if no predict_proba

        # Metrics
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        results.append({
            "Model": name,
            "Accuracy": acc,
            "F1-Score": f1,
            "ROC-AUC": roc_auc
        })

        print(f"{name:<25} | {acc:.4f}   | {f1:.4f}   | {roc_auc:.4f}")

        # Track best model based on F1-Score
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_model = model

    print("-" * 65)
    print(f"\n[+] Best Model Selected: {best_model_name} (F1-Score: {best_f1:.4f})")

    # 5. Save the best model
    if not os.path.exists(MODEL_SAVE_DIR):
        os.makedirs(MODEL_SAVE_DIR)

    with open(BEST_MODEL_PATH, 'wb') as f:
        pickle.dump(best_model, f)

    print(f"[+] Best model successfully saved to {BEST_MODEL_PATH}")


if __name__ == "__main__":
    train_and_evaluate()
