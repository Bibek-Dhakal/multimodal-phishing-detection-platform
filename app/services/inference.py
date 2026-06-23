import io
import json
from urllib.parse import urlparse

import numpy as np
import torch
from PIL import Image
from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool

from app.core.config import settings
from app.data_transformation import FeatureExtractor
from app.heuristics import calculate_entropy, is_whitelisted, check_brand_spoofing, calibrate_risk
from app.services.model_manager import registry
from app.threat_intel import get_threat_feed


async def run_multimodal_inference(features_str: str, url: str, image_bytes: bytes):
    """
    Core Business Logic layer for Threat Analysis.
    Decoupled from HTTP framework for clean architecture.
    """
    if not registry.ml_model or not registry.ann_model:
        raise HTTPException(status_code=500, detail="Core models are not loaded on the server.")

    if not features_str and not url:
        raise HTTPException(status_code=400, detail="Must provide either tabular features or a raw URL.")

    # --- 0. Layer 1 Threat Intelligence Bypass (OpenPhish) ---
    threat_pred = "Legitimate"
    threat_source = "Clean"
    domain_in = ""
    if url:
        try:
            parsed_in = urlparse(url if url.startswith('http') else 'http://' + url)
            domain_in = parsed_in.netloc.replace("www.", "").lower()

            for malicious_url in get_threat_feed():
                parsed_mal = urlparse(malicious_url)
                domain_mal = parsed_mal.netloc.replace("www.", "").lower()

                if domain_in and domain_in == domain_mal:
                    threat_pred = "Phishing"
                    threat_source = "OpenPhish"
                    break
        except Exception:
            pass

    # --- Feature Engineering (Async UI Non-Blocking) ---
    if features_str:
        try:
            features_list = json.loads(features_str)
        except Exception:
            raise HTTPException(status_code=400, detail="Features must be a valid JSON list string.")
    else:
        extractor = await run_in_threadpool(FeatureExtractor, url)
        features_list = await run_in_threadpool(extractor.extract_features)

    if len(features_list) != 30:
        raise HTTPException(status_code=400, detail=f"Expected 30 features, got {len(features_list)}")

    features_arr = np.array(features_list).reshape(1, -1)
    features_tensor = torch.tensor(features_arr, dtype=torch.float32)

    try:
        # --- 1. ML Prediction (XGBoost) ---
        if hasattr(registry.ml_model, "predict_proba"):
            ml_prob = float(registry.ml_model.predict_proba(features_arr)[0][1])
        else:
            ml_prob = float(registry.ml_model.predict(features_arr)[0])

        # --- 2. ANN Prediction (PyTorch) ---
        with torch.no_grad():
            ann_out = registry.ann_model(features_tensor)
            ann_prob = float(torch.sigmoid(ann_out).item())

        # --- 3. NLP Prediction ---
        nlp_pred = "Bypassed"
        nlp_prob = 0.0
        if url and registry.nlp_model:
            try:
                nlp_res = await run_in_threadpool(registry.nlp_model, url)
                label = nlp_res[0]['label']
                score = nlp_res[0]['score']
                nlp_prob = float(score) if label == 'LABEL_1' else float(1 - score)
                nlp_pred = "Phishing" if nlp_prob >= settings.PHISHING_THRESHOLD else "Legitimate"
            except Exception:
                nlp_pred = "Error"

        # --- 4. Vision Prediction ---
        vision_pred = "Bypassed"
        vision_prob = 0.0
        if image_bytes and registry.vision_model and registry.vision_preprocess:
            try:
                img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                img_t = registry.vision_preprocess(img).unsqueeze(0)

                with torch.no_grad():
                    out = registry.vision_model(img_t)
                    # Using pre-trained ImageNet model - index 1 (goldfish) acts as dummy validation
                    prob = torch.nn.functional.softmax(out, dim=1)[0][1].item()
                    vision_prob = float(prob)
                    vision_pred = "Phishing" if vision_prob >= settings.PHISHING_THRESHOLD else "Legitimate"
            except Exception:
                vision_pred = "Error"

        # --- 5. Priority Matrix & Calibrated Heuristics ---
        # XGBoost is deployed as the production standard for tabular feature sets
        xgb_weight = 1.0
        weighted_risk = ml_prob * xgb_weight

        continuous_metrics = {"length": 0, "entropy": 0.0, "penalty_applied": 0.0}

        if url:
            url_len = len(url)
            url_entropy = calculate_entropy(domain_in if domain_in else url)
            brand_spoof_penalty = check_brand_spoofing(domain_in)

            continuous_metrics["length"] = url_len
            continuous_metrics["entropy"] = round(url_entropy, 2)

            if domain_in and is_whitelisted(domain_in):
                weighted_risk = 0.01
            else:
                penalty = 0.0
                if url_len > 54:
                    penalty += min(0.15, (url_len - 54) * 0.002)
                if url_entropy > 4.0:
                    penalty += min(0.15, (url_entropy - 4.0) * 0.1)

                penalty += brand_spoof_penalty

                if image_bytes and vision_pred == "Phishing":
                    penalty += 0.20

                continuous_metrics["penalty_applied"] = round(penalty, 4)

                # Apply Calibrated Logistic Function 
                weighted_risk = calibrate_risk(weighted_risk, penalty)

        # --- 6. Tiered Alert Status ---
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
                "gate_logic": "XGBoost Production Standard (Logistic Calibrated)"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
