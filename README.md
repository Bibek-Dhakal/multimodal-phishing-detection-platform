# Multi-Modal Phishing Intelligence & Defense Platform

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Learning-ee4c2c)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)

## Project Overview

Phishing attacks remain one of the most pervasive cyber threats, causing billions of dollars in losses annually. This
project is a **Phishing Detection System** that automatically evaluates suspicious URLs using a production-grade *
*Layered Hybrid Defense Architecture**.

Instead of relying solely on isolated machine learning models, this platform combines:

1. **Live Threat Intelligence:** Integrates OpenPhish zero-day feeds via HTTPS/RDAP.
2. **Structural ML/DL Engines:** Benchmarks 8 traditional Machine Learning algorithms. **XGBoost** achieves top accuracy
   and serves as the primary production engine, while a custom PyTorch **Artificial Neural Network (ANN)** acts as a
   secondary experimental shadow model.
3. **Continuous Heuristics:** Uses Shannon Entropy, DuckDuckGo SERP indexing, and Fuzzy String Matching (Levenshtein
   Distance) to prevent false positives and catch zero-day typosquatting / brand spoofing.

The backend is modularized via FastAPI, containerized using Docker, and utilizes a Logistic Calibrated Matrix to
aggregate predictions and eliminate "alarm fatigue," displaying results through a Streamlit dashboard.

---

## Documentation

For a deep dive into the methodology and technical details, please refer to the following documents:

* [System Architecture](docs/architecture.md) - Details the Modular Data Pipeline, ML/DL Models, and App Deployment.
* [Dataset Information](docs/dataset_info.md) - Explains the UCI Phishing dataset features and structure.

---

## Architecture

1. **Threat Intelligence Layer**: Live TTL caching of the OpenPhish database and local Apex domain whitelisting.
2. **Production Machine Learning Engine**: Evaluates URLs structurally using the highly accurate XGBoost algorithm.
3. **Experimental Deep Learning Engine**: A Dense Multi-Layer Perceptron (MLP) built in PyTorch with Batch Normalization
   and Dropouts to evaluate non-linear patterns.
4. **Inference Services**: A decoupled FastAPI backend (`app/main.py` -> `app/services/`) that loads models via a
   Registry, applies Logistic Calibrated Penalties, and serves consensus predictions.
5. **User Interface**: Streamlit dashboard (`app/dashboard.py`) for security analysts to test web profile vectors and
   raw URLs natively.
6. **MLOps Orchestration**: Multi-container deployment managed via `docker-compose`.

---

## Installation & Setup

### 1. Prerequisites

- Docker and Docker Compose installed on your machine.
- *(Optional)* Python 3.9+ if running locally without Docker.

### 2. Running with Docker (Recommended)

The easiest way to boot the entire platform (both the FastAPI backend and Streamlit frontend) is using Docker Compose.

Ensure you have your models trained and saved in the `models/` folder (or run the training scripts first). Then execute:

```bash
docker-compose up --build
```

- The **FastAPI Backend** will be available at: http://localhost:8000
- The **Streamlit Dashboard** will be available at: http://localhost:8501

### 3. Local Development Setup (Without Docker)

Clone the repository and create a virtual environment:

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Train the models:

```bash
python train_ml.py
python train_ann.py
```

Run the application in two separate terminals:

**Terminal 1 (Backend):**

```bash
uvicorn app.main:app --reload
```

**Terminal 2 (Frontend):**

```bash
streamlit run app/dashboard.py
```

---

## Future Scope (Max Version)

The roadmap for this platform includes scaling into a Multi-Modal architecture:

* **NLP Linguistic Engine**: Integrating a fine-tuned `distilroberta-base` Transformer to analyze raw URL strings for
  malicious subdomains.
* **Computer Vision Engine**: Utilizing a pre-trained `EfficientNet-B0` CNN to analyze website screenshots for spatial
  layout anomalies and brand logo spoofing.

---
