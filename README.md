# Multi-Modal Phishing Intelligence & Defense Platform

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Learning-ee4c2c)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)

## Project Overview

Phishing attacks remain one of the most pervasive cyber threats. This project is a **Phishing Detection System** that
automatically evaluates suspicious URLs using a production-grade **Layered Multi-Modal Architecture**.

Instead of relying solely on isolated machine learning models, this platform utilizes a **Soft-Voting Fusion
Aggregator** that combines:

1. **Tabular Structural Intelligence (40% Weight):** An XGBoost production champion trained on the ISCX 2016 URL dataset
   to evaluate 79 mathematical and structural dimensions natively.
2. **Contextual Linguistic Intelligence (40% Weight):** A fine-tuned Hugging Face Deep Transformer (
   `microsoft/MiniLM-L12-H384-uncased`) evaluating the raw URL semantics and text sequences via attention masks.
3. **Visual Convolutional Intelligence (20% Weight):** A roadmap CNN pipeline tracking Playwright browser screenshots
   scaled for ImageNet tensors to catch brand spoofing.

The system is decoupled into strict microservice boundaries utilizing FastAPI for the backend gateway and Streamlit for
the user dashboard.

---

## Documentation

For a deep dive into the methodology and technical details, please refer to the following documents:

* [System Architecture](docs/ARCHITECTURE.md) - Details the Decoupled Service Topologies, NLP Transformer flows, and
  Soft-Voting Aggregation.
* [Data Registry & Provenance](docs/DATASETS.md) - Explains the ISCX tabular schema and the Kaggle PhiUSIIL NLP text
  structures.
* [Visual CNN Roadmap](docs/VISION_TODO.md) - The SSoT guide for downloading the PhishIntention CRP image sets and
  implementing the visual branch.

---

## Installation & Setup

### 1. Prerequisites

- **Python 3.12+** installed on your local machine (required for NumPy compatibility and initial model training).
- **Docker** and **Docker Compose** installed.

### 2. Local Setup & Model Training (Required First)

Before running the APIs or building containers, you must train the models locally so the weights are available in the
`models/` directory.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment (Windows):

```bash
.venv\Scripts\activate
```

Activate the environment (Mac/Linux):

```bash
source .venv/bin/activate
```

Install the strictly locked dependencies:

```bash
pip install -r requirements.min.versions.txt
```

*(Ensure you have placed the ISCX and PhiUSIIL datasets into the `data/` directory per the docs).*

Train the Tabular XGBoost model:

```bash
python src/train_tabular.py
```

Train the NLP MiniLM model:

```bash
python src/train_nlp.py
```

### 3. Local Development Setup (Running Without Docker)

Once models are trained, you can run the microservices locally in two separate terminals.

**Terminal 1 (Backend API):**

```bash
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 (Frontend UI):**

```bash
streamlit run app/ui.py --server.port 8501
```

### 4. Containerized Deployment (Running With Docker)

The easiest way to boot the entire platform securely for production is using Docker Compose. Make sure your models were
successfully saved in Step 2.

Copy the environment template:

```bash
cp .env.example .env
```

Build and spin up the microservices:

```bash
docker-compose up --build
```

- The **FastAPI Backend Gateway** will be available at: http://localhost:8000
- The **Streamlit User Dashboard** will be available at: http://localhost:8501

---
