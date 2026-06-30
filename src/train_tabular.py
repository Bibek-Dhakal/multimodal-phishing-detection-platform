import os
import pickle
import sys

from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from src.tabular_pipeline import prepare_iscx_dataset


def train_tabular_models():
    if not os.path.exists(settings.ISCX_CSV):
        print(f"[-] ISCX dataset missing at {settings.ISCX_CSV}. Please download it.")
        return

    print(f"[*] Loading ISCX dataset from {settings.ISCX_CSV}")
    X_train, X_test, y_train, y_test = prepare_iscx_dataset(settings.ISCX_CSV)

    # Gradient & Distance based models require scaling to converge properly and quickly.
    # Tree based models (Decision Tree, Random Forest, XGBoost) do not require scaling.
    models = {
        "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=42)),
        "Naive Bayes": make_pipeline(StandardScaler(), GaussianNB()),
        "KNN": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5)),
        "SVM": make_pipeline(StandardScaler(), CalibratedClassifierCV(SVC(random_state=42), ensemble=False)),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42),
        "AdaBoost": AdaBoostClassifier(random_state=42),
        "ANN (MLP)": make_pipeline(StandardScaler(),
                                   MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)),
        # PRO FIX: Wrapping XGBoost in a Calibrator to ensure organic probabilities (not just 100% or 0%)
        "XGBoost": CalibratedClassifierCV(XGBClassifier(eval_metric='logloss', random_state=42), method='sigmoid', cv=5)
    }

    best_f1 = 0
    best_model = None

    print("\n[*] Training and Evaluating Mathematical/Structural Models...")
    print("-" * 65)

    for name, model in models.items():
        try:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            if hasattr(model, "predict_proba"):
                y_proba = model.predict_proba(X_test)[:, 1]
                roc_auc = roc_auc_score(y_test, y_proba)
            else:
                roc_auc = roc_auc_score(y_test, y_pred)

            acc = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            print(f"{name:<20} | Acc: {acc:.4f} | F1: {f1:.4f} | AUC: {roc_auc:.4f}")

            if name == "XGBoost":
                best_model = model
        except Exception as e:
            print(f"{name:<20} | Training Failed: {str(e)}")

    if best_model:
        os.makedirs(os.path.dirname(settings.TABULAR_MODEL_PATH), exist_ok=True)
        with open(settings.TABULAR_MODEL_PATH, 'wb') as f:
            pickle.dump(best_model, f)
        print(f"\n[+] Production Champion (XGBoost) saved to {settings.TABULAR_MODEL_PATH}")


if __name__ == "__main__":
    train_tabular_models()