import os
import pickle

import numpy as np
import torch
import torch.nn as nn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Initialize FastAPI App
app = FastAPI(title="Phishing Detection API", description="Multi-Modal Threat Analysis Backend")


# Define the ANN Architecture (Must match exactly how it was trained)
class PhishingANN(nn.Module):
    def __init__(self, input_dim):
        super(PhishingANN, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1)
        )

    def forward(self, x):
        return self.network(x)


# Globals for models
ml_model = None
ann_model = None


# Pydantic Schema for Input
class TabularFeatures(BaseModel):
    features: list[int]


@app.on_event("startup")
def load_models():
    """Load both trained models into memory when the server starts."""
    global ml_model, ann_model

    ml_path = "models/best_traditional_ml.pkl"
    ann_path = "models/tabular_ann.pt"

    print("[*] Booting Inference Engines...")

    # Load ML Model (XGBoost)
    if os.path.exists(ml_path):
        with open(ml_path, "rb") as f:
            ml_model = pickle.load(f)
        print("[+] ML Model loaded.")
    else:
        print("[-] Warning: ML Model not found!")

    # Load DL Model (PyTorch ANN)
    if os.path.exists(ann_path):
        ann_model = PhishingANN(input_dim=30)
        # Using map_location='cpu' ensures it runs safely on any machine during inference
        ann_model.load_state_dict(torch.load(ann_path, map_location=torch.device('cpu')))
        ann_model.eval()
        print("[+] ANN Model loaded.")
    else:
        print("[-] Warning: ANN Model not found!")


@app.get("/")
def health_check():
    return {"status": "Active", "message": "Phishing Detection API is running."}


@app.post("/predict/tabular")
def predict_tabular(data: TabularFeatures):
    if not ml_model or not ann_model:
        raise HTTPException(status_code=500, detail="Models are not loaded on the server.")

    if len(data.features) != 30:
        raise HTTPException(status_code=400, detail=f"Expected 30 features, got {len(data.features)}")

    # Convert incoming list to Numpy Array & Tensor
    features_arr = np.array(data.features).reshape(1, -1)
    features_tensor = torch.tensor(features_arr, dtype=torch.float32)

    try:
        # --- 1. ML Prediction (XGBoost) ---
        if hasattr(ml_model, "predict_proba"):
            ml_prob = float(ml_model.predict_proba(features_arr)[0][1])
        else:
            ml_prob = float(ml_model.predict(features_arr)[0])

        ml_pred = "Phishing" if ml_prob >= 0.5 else "Legitimate"

        # --- 2. ANN Prediction (PyTorch) ---
        with torch.no_grad():
            ann_out = ann_model(features_tensor)
            ann_prob = float(torch.sigmoid(ann_out).item())

        ann_pred = "Phishing" if ann_prob >= 0.5 else "Legitimate"

        # --- 3. Consensus Logic ---
        avg_risk = (ml_prob + ann_prob) / 2
        consensus = "Phishing" if avg_risk >= 0.5 else "Legitimate"

        return {
            "ml_engine": {
                "prediction": ml_pred,
                "risk_score": round(ml_prob, 4)
            },
            "ann_engine": {
                "prediction": ann_pred,
                "risk_score": round(ann_prob, 4)
            },
            "consensus": {
                "final_decision": consensus,
                "average_risk": round(avg_risk, 4)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
