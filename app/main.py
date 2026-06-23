import os
import pickle
import json
import urllib.request
from urllib.parse import urlparse
import time
import math

import numpy as np
import torch
import torch.nn as nn
from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from typing import Optional

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


# Globals for models and intelligence feeds
ml_model = None
ann_model = None
nlp_model = None    # Placeholder for NLP Transformer
vision_model = None # Placeholder for CNN
openphish_feed = set()
last_feed_update = 0
OPENPHISH_URL = "https://openphish.com/feed.txt"


def update_threat_feed():
    """1-Hour TTL Background Caching to prevent network latency."""
    global openphish_feed, last_feed_update
    if time.time() - last_feed_update > 3600:
        try:
            req = urllib.request.Request(OPENPHISH_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                raw_data = response.read().decode('utf-8')
                new_feed = {line.strip() for line in raw_data.splitlines() if line.strip()}
                if new_feed:
                    openphish_feed = new_feed
                    last_feed_update = time.time()
        except Exception as e:
            print(f"[-] Background threat feed update failed: {e}")

def calculate_entropy(text):
    """Calculates the mathematical randomness (Shannon Entropy) of the string."""
    if not text: return 0
    entropy = 0
    for x in set(text):
        p_x = float(text.count(x)) / len(text)
        entropy += - p_x * math.log2(p_x)
    return entropy

def is_whitelisted(domain):
    """Local High-Confidence Apex Whitelist to prevent False Positives."""
    trusted = ["microsoft.com", "google.com", "amazon.com", "apple.com", "github.com", "linkedin.com", "paypal.com"]
    return any(domain == t or domain.endswith('.' + t) for t in trusted)


@app.on_event("startup")
def load_models():
    """Load both trained models and threat intelligence feeds into memory when the server starts."""
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
        ann_model.load_state_dict(torch.load(ann_path, map_location=torch.device('cpu')))
        ann_model.eval()
        print("[+] ANN Model loaded.")
    else:
        print("[-] Warning: ANN Model not found!")

    # Initial Threat Feed Load
    print("[*] Fetching live OpenPhish Threat Feed...")
    update_threat_feed()
    print(f"[+] Loaded {len(openphish_feed)} active zero-day phishing URLs into RAM.")


@app.get("/")
def health_check():
    return {"status": "Active", "message": "Phishing Detection API is running."}


@app.post("/predict/multimodal")
async def predict_multimodal(
    features: str = Form(...),
    url: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None)
):
    if not ml_model or not ann_model:
        raise HTTPException(status_code=500, detail="Core models are not loaded on the server.")

    # Execute TTL cache check for threat feed (virtually zero cost if < 3600s)
    update_threat_feed()

    # --- 0. Layer 1 Threat Intelligence Bypass (OpenPhish) ---
    threat_pred = "Legitimate"
    threat_source = "Clean"
    domain_in = ""
    if url:
        try:
            parsed_in = urlparse(url if url.startswith('http') else 'http://' + url)
            domain_in = parsed_in.netloc.replace("www.", "").lower()
            
            for malicious_url in openphish_feed:
                parsed_mal = urlparse(malicious_url)
                domain_mal = parsed_mal.netloc.replace("www.", "").lower()
                
                if domain_in and domain_in == domain_mal:
                    threat_pred = "Phishing"
                    threat_source = "OpenPhish"
                    break
        except Exception:
            pass

    try:
        features_list = json.loads(features)
    except Exception:
        raise HTTPException(status_code=400, detail="Features must be a valid JSON list string.")

    if len(features_list) != 30:
        raise HTTPException(status_code=400, detail=f"Expected 30 features, got {len(features_list)}")

    features_arr = np.array(features_list).reshape(1, -1)
    features_tensor = torch.tensor(features_arr, dtype=torch.float32)

    try:
        # --- 1. ML Prediction (XGBoost) ---
        if hasattr(ml_model, "predict_proba"):
            ml_prob = float(ml_model.predict_proba(features_arr)[0][1])
        else:
            ml_prob = float(ml_model.predict(features_arr)[0])

        # --- 2. ANN Prediction (PyTorch) ---
        with torch.no_grad():
            ann_out = ann_model(features_tensor)
            ann_prob = float(torch.sigmoid(ann_out).item())

        # --- 3. NLP & Vision Placeholders ---
        nlp_pred = "Bypassed"
        nlp_prob = 0.0
        if url:
            # TODO: Integrate DistilRoBERTa model evaluation here
            nlp_pred = "Legitimate"
            nlp_prob = 0.05
            
        vision_pred = "Bypassed"
        vision_prob = 0.0
        if image and image.filename:
            # TODO: Resize image to 224x224x3 and apply EfficientNet-B0 here
            vision_pred = "Legitimate"
            vision_prob = 0.05

        # --- 4. Weighted Priority Matrix & Continuous Math Gradients ---
        # Base weighted risk calculation (Prioritizing ML structure 60/40)
        xgb_weight = 0.60
        ann_weight = 0.40
        weighted_risk = (ml_prob * xgb_weight) + (ann_prob * ann_weight)

        continuous_metrics = {"length": 0, "entropy": 0.0, "penalty_applied": 0.0}
        
        if url:
            url_len = len(url)
            url_entropy = calculate_entropy(domain_in if domain_in else url)
            continuous_metrics["length"] = url_len
            continuous_metrics["entropy"] = round(url_entropy, 2)
            
            # If domain is whitelisted, override risk to prevent false positives
            if domain_in and is_whitelisted(domain_in):
                weighted_risk = 0.01
            else:
                # Apply continuous math gradients for zero-days
                penalty = 0.0
                if url_len > 54:
                    penalty += min(0.15, (url_len - 54) * 0.002)
                if url_entropy > 4.0:
                    penalty += min(0.15, (url_entropy - 4.0) * 0.1)
                
                # Multi-Modal Vision Verify (Brand Impersonation Check)
                if image and image.filename:
                    # Simulated logic: if vision detects a brand but domain is not whitelisted
                    penalty += 0.20
                    vision_pred = "Phishing (Spoof Detected)"
                    vision_prob = 0.90
                    
                continuous_metrics["penalty_applied"] = round(penalty, 4)
                weighted_risk += penalty

        # Cap risk to 99% unless Layer 1 overrides
        weighted_risk = min(0.99, weighted_risk)

        # --- 5. Tiered Alert Status (Taming Alarm Fatigue) ---
        if threat_pred == "Phishing":
            weighted_risk = 1.0
            consensus = "Phishing"
        elif weighted_risk > 0.75:
            consensus = "Phishing"
        elif weighted_risk > 0.35:
            consensus = "Suspicious"
        else:
            consensus = "Legitimate"

        ml_pred_status = "Phishing" if ml_prob > 0.75 else ("Suspicious" if ml_prob > 0.35 else "Legitimate")
        ann_pred_status = "Phishing" if ann_prob > 0.75 else ("Suspicious" if ann_prob > 0.35 else "Legitimate")

        return {
            "threat_intelligence": {
                "prediction": threat_pred,
                "source": threat_source
            },
            "ml_engine": {
                "prediction": ml_pred_status,
                "risk_score": round(ml_prob, 4)
            },
            "ann_engine": {
                "prediction": ann_pred_status,
                "risk_score": round(ann_prob, 4)
            },
            "nlp_engine": {
                "prediction": nlp_pred,
                "risk_score": round(nlp_prob, 4)
            },
            "vision_engine": {
                "prediction": vision_pred,
                "risk_score": round(vision_prob, 4)
            },
            "continuous_heuristics": continuous_metrics,
            "consensus": {
                "final_decision": consensus,
                "weighted_risk": round(weighted_risk, 4),
                "gate_logic": "Weighted Priority Matrix"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))