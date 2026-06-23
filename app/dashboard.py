import json
import os
import sys

import requests
import streamlit as st

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Ensure the app directory is in the system path for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuration
API_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000/predict/multimodal")

st.set_page_config(page_title="Phishing Defense Platform", page_icon="🛡️", layout="wide")

st.title("🛡️ Multi-Modal Phishing Intelligence & Defense")
st.markdown("""
This platform uses advanced **Machine Learning (XGBoost)** and **Deep Learning (PyTorch ANN)** to evaluate structural indicators from website URLs and HTML content to detect phishing attacks.
""")

st.divider()

st.subheader("1. Ingestion Layer (Exclusive Select One)")
ingestion_mode = st.radio(
    "Select Input Mode",
    ["URL Input", "Manual Form", "JSON Payload"],
    horizontal=True,
    help="Exclusive selection for structural feature ingestion."
)

# Helper dictionary to map user-friendly text to model integer values
opt_map = {"Legitimate": 1, "Suspicious": 0, "Phishing": -1}


def create_selectbox(label, options=["Legitimate", "Phishing"]):
    return st.selectbox(label, options=options)


current_features = None
trigger_analysis = False
raw_url = ""

if ingestion_mode == "URL Input":
    st.markdown("**Automated Feature Extraction (Asynchronous)**")
    raw_url = st.text_input("Raw URL String", placeholder="https://example.com")
    if st.button("🚀 Extract & Analyze", use_container_width=True):
        if raw_url:
            # Backend handles the extraction asynchronously to avoid UI freezing
            current_features = None
            trigger_analysis = True
        else:
            st.error("Please enter a valid URL.")

elif ingestion_mode == "Manual Form":
    st.markdown("**Manual Web Profile Vectors**")
    raw_url = st.text_input("Catch-All Raw URL String (For Threat Intel & Linguistic Evaluation)",
                            placeholder="Optional raw URL...")
    with st.form("feature_input_form"):
        tab1, tab2, tab3 = st.tabs(
            ["🌐 Address Bar & URL Features", "💻 HTML & JavaScript Features", "🌍 Domain & External Features"])

        with tab1:
            st.markdown("**URL Structural Anomalies**")
            col1, col2, col3 = st.columns(3)
            with col1:
                f1 = create_selectbox("IP Address in URL (having_IP_Address)")
                f2 = create_selectbox("URL Length (URL_Length)", ["Legitimate", "Suspicious", "Phishing"])
                f3 = create_selectbox("Shortening Service (Shortining_Service)")
                f4 = create_selectbox("@ Symbol (having_At_Symbol)")
            with col2:
                f5 = create_selectbox("Double Slash Redirect (double_slash_redirecting)")
                f6 = create_selectbox("Prefix/Suffix using '-' (Prefix_Suffix)")
                f7 = create_selectbox("Sub Domains (having_Sub_Domain)", ["Legitimate", "Suspicious", "Phishing"])
                f8 = create_selectbox("SSL Final State (SSLfinal_State)", ["Legitimate", "Suspicious", "Phishing"])
            with col3:
                f9 = create_selectbox("Domain Registration Length (Domain_registeration_length)")
                f10 = create_selectbox("External Favicon (Favicon)")
                f11 = create_selectbox("Non-Standard Port (port)")
                f12 = create_selectbox("HTTPS Token in URL (HTTPS_token)")

        with tab2:
            st.markdown("**Webpage Behavior & Scripting**")
            col1, col2, col3 = st.columns(3)
            with col1:
                f13 = create_selectbox("Request URL (Request_URL)")
                f14 = create_selectbox("URL of Anchor (URL_of_Anchor)", ["Legitimate", "Suspicious", "Phishing"])
                f15 = create_selectbox("Links in Tags (Links_in_tags)", ["Legitimate", "Suspicious", "Phishing"])
                f16 = create_selectbox("Server Form Handler (SFH)", ["Legitimate", "Suspicious", "Phishing"])
            with col2:
                f17 = create_selectbox("Submitting to Email (Submitting_to_email)")
                f18 = create_selectbox("Abnormal URL (Abnormal_URL)")
                f19 = create_selectbox("Redirects (Redirect)", ["Legitimate", "Phishing"])  # 0, 1 in original
                f20 = create_selectbox("On Mouseover Event (on_mouseover)")
            with col3:
                f21 = create_selectbox("Right Click Disabled (RightClick)")
                f22 = create_selectbox("PopUp Window (popUpWidnow)")
                f23 = create_selectbox("IFrame Hidden (Iframe)")

        with tab3:
            st.markdown("**External Context & Ranking**")
            col1, col2, col3 = st.columns(3)
            with col1:
                f24 = create_selectbox("Age of Domain (age_of_domain)")
                f25 = create_selectbox("DNS Record (DNSRecord)")
            with col2:
                f26 = create_selectbox("Web Traffic (web_traffic)", ["Legitimate", "Suspicious", "Phishing"])
                f27 = create_selectbox("Page Rank (Page_Rank)")
            with col3:
                f28 = create_selectbox("Google Index (Google_Index)")
                f29 = create_selectbox("Links Pointing to Page (Links_pointing_to_page)",
                                       ["Legitimate", "Suspicious", "Phishing"])
                f30 = create_selectbox("Statistical Report (Statistical_report)")

        analyze_btn = st.form_submit_button("🚀 Run Threat Analysis", use_container_width=True)

        if analyze_btn:
            redirect_val = 0 if f19 == "Legitimate" else 1

            current_features = [
                opt_map[f1], opt_map[f2], opt_map[f3], opt_map[f4], opt_map[f5], opt_map[f6],
                opt_map[f7], opt_map[f8], opt_map[f9], opt_map[f10], opt_map[f11], opt_map[f12],
                opt_map[f13], opt_map[f14], opt_map[f15], opt_map[f16], opt_map[f17], opt_map[f18],
                redirect_val, opt_map[f20], opt_map[f21], opt_map[f22], opt_map[f23], opt_map[f24],
                opt_map[f25], opt_map[f26], opt_map[f27], opt_map[f28], opt_map[f29], opt_map[f30]
            ]
            trigger_analysis = True

elif ingestion_mode == "JSON Payload":
    st.markdown("**API JSON Payload**")
    raw_url = st.text_input("Catch-All Raw URL String (For Threat Intel & Linguistic Evaluation)",
                            placeholder="Optional raw URL...")
    json_input = st.text_area("Tabular Features Array (Length 30)", placeholder="[1, -1, 0, 1, 1, ...]")
    if st.button("🚀 Run Threat Analysis", use_container_width=True):
        try:
            parsed = json.loads(json_input)
            if isinstance(parsed, list) and len(parsed) == 30:
                current_features = parsed
                trigger_analysis = True
            else:
                st.error("Invalid payload: Must be a JSON list of exactly 30 integers.")
        except Exception as e:
            st.error(f"JSON Parse Error: {str(e)}")

st.divider()

st.subheader("2. Multi-Modal Sensors (Optional)")
col1, col2 = st.columns(2)
with col1:
    enable_nlp = st.checkbox("Enable Linguistic Evaluation (NLP Transformer)", value=True)
    if enable_nlp:
        st.info("NLP Engine is active (Depends on local Transformers availability).")

with col2:
    uploaded_file = st.file_uploader("Upload Webpage Screenshot (CNN Vision Engine)", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        st.info("Visual CNN Engine is active (Depends on local Torchvision availability).")

if trigger_analysis:
    with st.spinner("Engaging Neural Networks, ML Trees, and Threat Feeds asynchronously..."):
        try:
            payload_data = {}
            if current_features is not None:
                payload_data["features"] = json.dumps(current_features)

            payload_files = {}

            if raw_url:
                payload_data["url"] = raw_url

            if uploaded_file is not None:
                payload_files["image"] = (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)

            # Send data to FastAPI Backend
            response = requests.post(API_URL, data=payload_data, files=payload_files if payload_files else None)

            if response.status_code == 200:
                results = response.json()

                st.divider()
                st.subheader("3. Production Intelligence Report")

                metric_col1, metric_col2, metric_col3 = st.columns(3)

                threat_pred = results.get('threat_intelligence', {}).get('prediction', 'Legitimate')
                threat_source = results.get('threat_intelligence', {}).get('source', 'Clean')

                ml_pred = results['ml_engine']['prediction']
                ml_risk = results['ml_engine']['risk_score'] * 100

                cons_pred = results['consensus']['final_decision']
                cons_risk = results['consensus']['weighted_risk'] * 100

                nlp_pred = results['nlp_engine']['prediction']
                vision_pred = results['vision_engine']['prediction']
                ann_pred = results['ann_engine']['prediction']
                ann_risk = results['ann_engine']['risk_score'] * 100


                def get_icon(pred):
                    if "Phishing" in pred: return "🔴"
                    if "Suspicious" in pred: return "🟠"
                    if pred == "Legitimate": return "🟢"
                    return "⚪"


                threat_color = get_icon(threat_pred)
                ml_color = get_icon(ml_pred)
                cons_color = get_icon(cons_pred)
                ann_color = get_icon(ann_pred)

                with metric_col1:
                    st.metric(label=f"Live Threat Feed {threat_color}", value=threat_pred, delta=threat_source,
                              delta_color="off")

                with metric_col2:
                    st.metric(label=f"XGBoost Engine {ml_color}", value=ml_pred, delta=f"Risk: {ml_risk:.1f}%",
                              delta_color="inverse")

                with metric_col3:
                    st.metric(label=f"Production Consensus {cons_color}", value=cons_pred,
                              delta=f"Risk: {cons_risk:.1f}%", delta_color="inverse")

                st.divider()
                if cons_pred == "Phishing":
                    st.error(
                        f"**GLOBAL THREAT ALERT:** High probability malicious target. Logistic Calibrated Risk: {cons_risk:.1f}%")
                elif cons_pred == "Suspicious":
                    st.warning(
                        f"**SUSPICIOUS ACTIVITY FLAGGED:** Structural anomalies detected. Verification recommended. Logistic Calibrated Risk: {cons_risk:.1f}%")
                else:
                    st.success(
                        f"**TARGET SECURE:** URL satisfies core structural integrity benchmarks. Logistic Calibrated Risk: {cons_risk:.1f}%")

                st.divider()
                st.subheader("4. Experimental AI Lab (Secondary Opinions)")
                st.info(
                    "The custom PyTorch ANN is included as an experimental shadow model to demonstrate custom deep learning framework implementation, while XGBoost rules the tabular production environment.")

                exp_col1, exp_col2, exp_col3 = st.columns(3)

                with exp_col1:
                    st.metric(label=f"PyTorch ANN {ann_color}", value=ann_pred, delta=f"Risk: {ann_risk:.1f}%",
                              delta_color="inverse")

                with exp_col2:
                    if nlp_pred != "Bypassed":
                        nlp_risk = results['nlp_engine']['risk_score'] * 100
                        st.metric(label=f"NLP Engine {get_icon(nlp_pred)}", value=nlp_pred,
                                  delta=f"Risk: {nlp_risk:.1f}%", delta_color="inverse")
                    else:
                        st.metric(label="NLP Engine ⚪", value="Bypassed", delta="Inactive", delta_color="off")

                with exp_col3:
                    if vision_pred != "Bypassed":
                        vision_risk = results['vision_engine']['risk_score'] * 100
                        st.metric(label=f"Vision CNN {get_icon(vision_pred)}", value=vision_pred,
                                  delta=f"Risk: {vision_risk:.1f}%", delta_color="inverse")
                    else:
                        st.metric(label="Vision CNN ⚪", value="Bypassed", delta="Inactive", delta_color="off")

            else:
                st.error(f"Backend Error {response.status_code}: {response.json().get('detail', response.text)}")

        except requests.exceptions.ConnectionError:
            st.error(
                "🚨 Cannot connect to Backend Engine! Please make sure you ran 'uvicorn app.main:app --reload' in a separate terminal.")
