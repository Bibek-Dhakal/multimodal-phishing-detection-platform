import streamlit as st
import requests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

st.set_page_config(page_title="Phishing Defense Platform", page_icon="🛡️", layout="centered")

st.title("🛡️ Multi-Modal Phishing Intelligence & Defense")
st.markdown("""
This platform uses **Soft-Voting Ensembled Intelligence** combining:
1. **Structural XGBoost ML Engine** (Trained on ISCX offline variables)
2. **Contextual MiniLM Transformer** (Trained on Kaggle PhiUSIIL semantics)
3. **Visual CNN Engine** (Roadmap CNN layout screening)
""")

st.info("ℹ️ **Roadmap Notice:** The Visual CNN Engine (Playwright + EfficientNet) is currently in active development. Any CNN scores shown in the UI are mocked placeholders (TODO).")

url_input = st.text_input("Enter a suspicious URL to analyze:", placeholder="https://secure-login.verify.com")

if st.button("🚀 Analyze Threat Level", use_container_width=True):
    if url_input:
        with st.spinner("Executing Parallel AI Multi-Modal Pipelines..."):
            try:
                response = requests.post(settings.API_ENDPOINT_URL, json={"url": url_input}, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    
                    st.divider()
                    st.subheader("Aggregated Intelligence Report")
                    
                    verdict = result["verdict"]
                    risk_score = result["unified_risk_score"] * 100
                    
                    if verdict == "Phishing":
                        st.error(f"**CRITICAL THREAT DETECTED:** {risk_score:.1f}% Risk Probability")
                    elif verdict == "Suspicious":
                        st.warning(f"**WARNING:** {risk_score:.1f}% Risk Probability")
                    else:
                        st.success(f"**SECURE DOMAIN:** {risk_score:.1f}% Risk Probability")
                        
                    st.markdown("### Branch Component Breakdown")
                    c1, c2, c3 = st.columns(3)
                    c1.metric(
                        "Tabular (XGBoost)", 
                        f"{result['components']['tabular_xgboost_probability']*100:.1f}%", 
                        help="Predictive evaluation based purely on 79 structural variables"
                    )
                    c2.metric(
                        "NLP (MiniLM)", 
                        f"{result['components']['nlp_transformer_probability']*100:.1f}%", 
                        help="Attention-based linguistic semantic evaluation"
                    )
                    c3.metric(
                        "Vision (CNN)", 
                        f"{result['components']['vision_cnn_probability']*100:.1f}% (MOCKED)", 
                        help="TODO: Visual CNN Engine is currently inactive. This is a mocked placeholder."
                    )
                    
                else:
                    st.error(f"Backend Gateway Error: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error(f"🚨 Cannot connect to Backend! Ensure FastAPI is running at `{settings.API_ENDPOINT_URL}`.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
    else:
        st.error("Please enter a valid URL String.")