import requests
import streamlit as st

# Configuration
API_URL = "http://127.0.0.1:8000/predict/tabular"

st.set_page_config(page_title="Phishing Defense Platform", page_icon="🛡️", layout="wide")

st.title("🛡️ Multi-Modal Phishing Intelligence & Defense")
st.markdown("""
This platform uses advanced **Machine Learning (XGBoost)** and **Deep Learning (PyTorch ANN)** to evaluate structural indicators from website URLs and HTML content to detect phishing attacks.
""")

st.divider()

st.subheader("Tabular Analysis Engine (Structured Features)")

# For demonstration, we use two sample arrays pulled directly from the ARFF dataset
# Sample 1: A known phishing website
phishing_sample = [-1, 1, 1, 1, -1, -1, -1, -1, -1, 1, 1, -1, 1, -1, 1, -1, -1, -1, 0, 1, 1, 1, 1, -1, -1, -1, -1, 1, 1,
                   -1]
# Sample 2: A known legitimate website
legitimate_sample = [1, 0, -1, 1, 1, -1, 1, 1, -1, 1, 1, 1, 1, 0, 0, -1, 1, 1, 0, -1, 1, -1, 1, -1, -1, 0, -1, 1, 1, 1]

col1, col2 = st.columns([2, 1])

with col1:
    sample_choice = st.selectbox(
        "Select a Web Profile to Analyze:",
        [
            "Target A (Suspicious Activity Detected)",
            "Target B (Standard Corporate Website)"
        ]
    )

    if sample_choice == "Target A (Suspicious Activity Detected)":
        current_features = phishing_sample
        st.info("Loaded features typically indicating hidden iframes, external favicons, and abnormal URL requests.")
    else:
        current_features = legitimate_sample
        st.success("Loaded features typically indicating valid SSL certificates, standard ports, and trusted domains.")

with col2:
    st.write("")
    st.write("")
    analyze_btn = st.button("🚀 Run Threat Analysis", use_container_width=True)

if analyze_btn:
    with st.spinner("Engaging Neural Networks and ML Trees..."):
        try:
            # Send data to FastAPI Backend
            payload = {"features": current_features}
            response = requests.post(API_URL, json=payload)

            if response.status_code == 200:
                results = response.json()

                st.divider()
                st.subheader("Intelligence Report")

                # Display Metrics
                metric_col1, metric_col2, metric_col3 = st.columns(3)

                ml_pred = results['ml_engine']['prediction']
                ml_risk = results['ml_engine']['risk_score'] * 100

                ann_pred = results['ann_engine']['prediction']
                ann_risk = results['ann_engine']['risk_score'] * 100

                cons_pred = results['consensus']['final_decision']
                cons_risk = results['consensus']['average_risk'] * 100

                # Colors
                ml_color = "🔴" if ml_pred == "Phishing" else "🟢"
                ann_color = "🔴" if ann_pred == "Phishing" else "🟢"
                cons_color = "🔴" if cons_pred == "Phishing" else "🟢"

                with metric_col1:
                    st.metric(label=f"XGBoost Engine {ml_color}", value=ml_pred, delta=f"Risk: {ml_risk:.1f}%",
                              delta_color="inverse")

                with metric_col2:
                    st.metric(label=f"PyTorch ANN {ann_color}", value=ann_pred, delta=f"Risk: {ann_risk:.1f}%",
                              delta_color="inverse")

                with metric_col3:
                    st.metric(label=f"System Consensus {cons_color}", value=cons_pred,
                              delta=f"Overall Risk: {cons_risk:.1f}%", delta_color="inverse")

                if cons_pred == "Phishing":
                    st.error(
                        f"**WARNING:** The Consensus Engine has flagged this target as malicious. Probability of spoofing: {cons_risk:.1f}%")
                else:
                    st.success(
                        f"**SAFE:** The target exhibits structural integrity. Probability of spoofing: {cons_risk:.1f}%")

            else:
                st.error(f"Backend Error {response.status_code}: {response.text}")

        except requests.exceptions.ConnectionError:
            st.error(
                "🚨 Cannot connect to Backend Engine! Please make sure you ran 'uvicorn app.main:app --reload' in a separate terminal.")
