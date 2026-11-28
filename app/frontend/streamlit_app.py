import os
import time

import requests
import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="ChurnAI | Customer Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")



# =========================================================
# PREMIUM DARK SAAS THEME
# =========================================================

st.markdown(
    """
    <style>
    :root {
        --bg: #0B1120;
        --panel: #111C30;
        --panel-soft: #172337;
        --border: #263650;
        --text: #E5E7EB;
        --muted: #94A3B8;
        --blue: #3B82F6;
    }

    .stApp {
        background: var(--bg);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: rgba(11, 17, 32, 0.88);
    }

    [data-testid="stSidebar"] {
        background: #0E1728;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #CBD5E1;
    }

    h1, h2, h3, h4 {
        color: #F8FAFC !important;
        letter-spacing: -0.025em;
    }

    p, label, .stCaption {
        color: var(--muted);
    }

    .hero {
        padding: 26px 28px;
        border: 1px solid #29466F;
        border-radius: 18px;
        background: linear-gradient(120deg, #142744 0%, #111C30 58%, #172337 100%);
        margin: 8px 0 24px 0;
    }

    .hero-kicker {
        color: #93C5FD;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .hero-title {
        color: #F8FAFC;
        font-size: 2rem;
        line-height: 1.15;
        font-weight: 750;
        margin-bottom: 10px;
    }

    .hero-copy {
        color: #B6C4D8;
        font-size: 1rem;
        max-width: 760px;
        margin-bottom: 0;
    }

    .section-kicker {
        color: #60A5FA;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 5px;
    }

    .info-card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 18px;
        min-height: 138px;
    }

    .info-card-title {
        color: #F8FAFC;
        font-size: 1rem;
        font-weight: 650;
        margin-bottom: 8px;
    }

    .info-card-copy {
        color: #9CAEC4;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    div[data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--border);
        padding: 17px 18px;
        border-radius: 14px;
    }

    div[data-testid="stMetric"] label {
        color: #9CAEC4 !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 14px;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"] {
        background: #172337;
        border-color: #334155;
        border-radius: 9px;
        color: #E5E7EB;
    }

    input, textarea {
        color: #F8FAFC !important;
    }

    .stButton > button,
    .stFormSubmitButton > button,
    [data-testid="stFormSubmitButton"] button {
        background: #2563EB !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        opacity: 1 !important;
        border: 1px solid #3B82F6 !important;
        border-radius: 10px;
        min-height: 48px;
        font-weight: 750 !important;
        font-size: 16px !important;
        letter-spacing: 0.2px;
        transition: 0.15s ease;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover,
    [data-testid="stFormSubmitButton"] button:hover {
        background: #1D4ED8 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border-color: #60A5FA !important;
    }

    .stButton > button:disabled,
    .stFormSubmitButton > button:disabled,
    [data-testid="stFormSubmitButton"] button:disabled {
        background: #2563EB !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        opacity: 1 !important;
    }

    [data-testid="stProgressBar"] > div > div {
        background: #3B82F6;
    }

    hr {
        border-color: var(--border);
    }

    [data-testid="stAlert"] {
        border-radius: 11px;
    }

    .sidebar-brand {
        padding: 8px 4px 18px 4px;
    }

    .sidebar-brand-name {
        color: #F8FAFC;
        font-size: 1.25rem;
        font-weight: 800;
        letter-spacing: -0.03em;
    }

    .sidebar-brand-sub {
        color: #8294AD;
        font-size: 0.76rem;
        margin-top: 3px;
    }

    .muted-note {
        color: #8294AD;
        font-size: 0.82rem;
    }

    @media (max-width: 768px) {
        .hero {
            padding: 20px;
        }
        .hero-title {
            font-size: 1.55rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)




# =========================================================
# AUTHENTICATION + API HELPERS
# =========================================================

def api_request(method, endpoint, *, token=None, **kwargs):
    headers = kwargs.pop("headers", {}) or {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    last_error = None
    for attempt in range(3):
        try:
            response = requests.request(
                method, f"{API_BASE_URL}{endpoint}", headers=headers, timeout=90, **kwargs
            )
            if response.status_code not in (502, 503, 504) or attempt == 2:
                return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
            last_error = exc
            if attempt == 2:
                raise
        if attempt < 2:
            time.sleep(5)
    if last_error:
        raise last_error
    return response

def show_api_error(response, action):
    try:
        detail = response.json().get("detail", response.text)
    except ValueError:
        detail = response.text
    st.error(f"{action} failed (HTTP {response.status_code}): {detail}")

def auth_screen():
    st.markdown('<div class="hero"><div class="hero-kicker">Secure workspace</div><div class="hero-title">Welcome to ChurnAI</div><p class="hero-copy">Sign in to access your customer intelligence workspace and private prediction history.</p></div>', unsafe_allow_html=True)
    left, center, right = st.columns([1, 1.25, 1])
    with center:
        login_tab, signup_tab = st.tabs(["Sign in", "Create account"])
        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Email address", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                submit = st.form_submit_button("Sign in", use_container_width=True)
            if submit:
                if not email.strip() or not password:
                    st.error("Enter your email and password.")
                else:
                    try:
                        with st.spinner("Signing you in..."):
                            response = api_request("POST", "/auth/login", json={"email": email.strip(), "password": password})
                        if response.status_code == 200:
                            payload = response.json()
                            st.session_state["auth_token"] = payload["access_token"]
                            st.session_state["auth_user"] = payload["user"]
                            st.rerun()
                        else:
                            show_api_error(response, "Sign in")
                    except requests.exceptions.RequestException:
                        st.error("Could not reach the backend. Check that the API is running and try again.")
        with signup_tab:
            with st.form("signup_form"):
                name = st.text_input("Full name", key="signup_name")
                new_email = st.text_input("Email address", key="signup_email")
                new_password = st.text_input("Password", type="password", key="signup_password")
                confirm_password = st.text_input("Confirm password", type="password", key="signup_confirm")
                create = st.form_submit_button("Create account", use_container_width=True)
            if create:
                if not name.strip() or not new_email.strip() or not new_password:
                    st.error("Complete all fields.")
                elif len(new_password) < 8:
                    st.error("Password must contain at least 8 characters.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    try:
                        with st.spinner("Creating your account..."):
                            response = api_request("POST", "/auth/signup", json={"name": name.strip(), "email": new_email.strip(), "password": new_password})
                        if response.status_code == 200:
                            payload = response.json()
                            st.session_state["auth_token"] = payload["access_token"]
                            st.session_state["auth_user"] = payload["user"]
                            st.rerun()
                        else:
                            show_api_error(response, "Account creation")
                    except requests.exceptions.RequestException:
                        st.error("Could not reach the backend. Check that the API is running and try again.")
    st.caption("Your account and prediction history are stored securely in the connected database.")


# =========================================================
# HELPERS
# =========================================================

def format_feature_name(name):
    name = name.replace("num__", "").replace("cat__", "")

    mappings = {
        "tenure": "Customer Tenure",
        "SeniorCitizen": "Senior Citizen",
        "MonthlyCharges": "Monthly Charges",
        "TotalCharges": "Total Charges",
        "Contract": "Contract",
        "InternetService": "Internet Service",
        "PaymentMethod": "Payment Method",
        "OnlineSecurity": "Online Security",
        "OnlineBackup": "Online Backup",
        "DeviceProtection": "Device Protection",
        "TechSupport": "Tech Support",
        "StreamingTV": "Streaming TV",
        "StreamingMovies": "Streaming Movies",
        "PaperlessBilling": "Paperless Billing",
        "MultipleLines": "Multiple Lines",
        "PhoneService": "Phone Service",
        "Dependents": "Dependents",
        "Partner": "Partner",
        "gender": "Gender",
    }

    for original, readable in mappings.items():
        if name.startswith(original + "_"):
            value = name[len(original) + 1:].replace("_", " ")
            return f"{readable}: {value.title()}"
        if name == original:
            return readable

    return name.replace("_", " ").title()


def request_prediction(customer_data):
    """Send prediction request with bounded retries for Render cold starts."""
    response = None

    for attempt in range(3):
        try:
            response = requests.post(
                f"{API_BASE_URL}/predict",
                json=customer_data,
                timeout=90,
            )

            if response.status_code not in (502, 503, 504):
                return response

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            if attempt == 2:
                raise

        if attempt < 2:
            st.warning(
                f"Backend is waking up. Retrying ({attempt + 1}/2)..."
            )
            time.sleep(10)

    return response


def render_prediction_result(result):
    churn_probability = float(result["churn_probability"])
    prediction = result["prediction"]
    risk_level = result.get("risk_level", "Unknown")
    threshold = result["threshold"]
    recommendations = result.get("recommendations", [])

    st.markdown('<div class="section-kicker">Model output</div>', unsafe_allow_html=True)
    st.header("Prediction result")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Churn probability", f"{churn_probability * 100:.2f}%")
    with col2:
        st.metric("Risk level", risk_level)
    with col3:
        st.metric("Prediction", "Churn" if prediction == 1 else "No churn")

    if risk_level == "High":
        st.error("High churn risk detected. Consider proactive retention action.")
    elif risk_level == "Moderate":
        st.warning("Moderate churn risk detected. Monitor this customer.")
    else:
        st.success("Low churn risk detected.")

    st.progress(min(max(churn_probability, 0.0), 1.0))
    st.caption(f"Decision threshold used: {float(threshold):.4f}")

    st.divider()
    st.subheader("Retention recommendations")

    if recommendations:
        for recommendation in recommendations:
            st.info(f"📌 {recommendation}")
    else:
        st.write("No recommendations available for this prediction.")

    st.divider()
    st.subheader("Why did the model make this prediction?")
    st.caption(
        "These factors show which customer attributes influenced the "
        "prediction and the direction of their impact."
    )

    factors = result.get("top_churn_factors", [])

    if not factors:
        st.info("No SHAP explanation is available for this prediction.")
        return

    max_impact = max(
        (abs(float(factor.get("impact", 0))) for factor in factors),
        default=0.0,
    )

    for factor in factors:
        feature = format_feature_name(factor["feature"])
        impact = float(factor["impact"])
        direction = factor.get("direction", "Impact unavailable")
        normalized_impact = abs(impact) / max_impact if max_impact > 0 else 0.0

        with st.container(border=True):
            left, right = st.columns([3, 1])
            with left:
                st.markdown(f"**{feature}**")
                if impact > 0:
                    st.error(f"🔴 {direction}")
                elif impact < 0:
                    st.success(f"🟢 {direction}")
                else:
                    st.info("⚪ No directional impact")
            with right:
                st.metric("SHAP impact", f"{impact:+.4f}")

            st.progress(min(max(normalized_impact, 0.0), 1.0))


# =========================================================
# AUTHENTICATED WORKSPACE
# =========================================================

if not st.session_state.get("auth_token"):
    auth_screen()
    st.stop()

# Validate token on each fresh Streamlit session / rerun.
if not st.session_state.get("auth_user"):
    try:
        me = api_request("GET", "/auth/me", token=st.session_state["auth_token"])
        if me.status_code == 200:
            st.session_state["auth_user"] = me.json()
        else:
            st.session_state.pop("auth_token", None)
            st.session_state.pop("auth_user", None)
            st.warning("Your session expired. Please sign in again.")
            st.rerun()
    except requests.exceptions.RequestException:
        st.error("Unable to validate your session because the backend is unavailable.")
        st.stop()

user = st.session_state["auth_user"]
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand"><div class="sidebar-brand-name">✦ ChurnAI</div>
    <div class="sidebar-brand-sub">Customer intelligence platform</div></div>
    """, unsafe_allow_html=True)
    st.caption(f"Signed in as {user.get('name', 'User')}")
    st.markdown("### WORKSPACE")
    page = st.radio("Navigation", ["Overview", "Predict Churn", "Prediction History", "AI Insights"], label_visibility="collapsed")
    st.divider()
    if st.button("Log out", use_container_width=True):
        for key in ["auth_token", "auth_user", "latest_prediction", "latest_customer"]:
            st.session_state.pop(key, None)
        st.rerun()
    st.markdown("### SYSTEM")
    st.markdown('<div class="muted-note">Prediction engine · FastAPI</div><div class="muted-note">Model explainability · SHAP</div><div class="muted-note">Private account history · Supabase</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<div class="muted-note">Customer Churn AI · v2.0</div>', unsafe_allow_html=True)


def fetch_history():
    response = api_request("GET", "/history?limit=100", token=st.session_state["auth_token"])
    if response.status_code == 200:
        return response.json()
    if response.status_code == 401:
        st.session_state.pop("auth_token", None)
        st.session_state.pop("auth_user", None)
        st.warning("Session expired. Sign in again.")
        st.rerun()
    show_api_error(response, "Loading prediction history")
    return []


if page == "Overview":
    st.markdown("<div class='hero'><div class='hero-kicker'>Customer intelligence workspace</div><div class='hero-title'>Understand churn before it happens.</div><p class='hero-copy'>Predict customer churn risk, understand the factors behind each prediction, and identify practical retention actions.</p></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">Workspace</div>', unsafe_allow_html=True)
    st.header("Your churn analysis toolkit")
    c1, c2, c3 = st.columns(3)
    cards = [("🎯 Churn prediction", "Evaluate a customer's churn probability using their profile, services, contract and billing information."), ("🔍 Explainable AI", "Review the SHAP factors that influenced the model's prediction and understand their direction."), ("💡 Retention actions", "Use model-generated recommendations to help prioritize customer retention efforts.")]
    for col, (title, copy) in zip((c1,c2,c3), cards):
        with col:
            st.markdown(f'<div class="info-card"><div class="info-card-title">{title}</div><div class="info-card-copy">{copy}</div></div>', unsafe_allow_html=True)
    st.write("")
    try:
        history = fetch_history()
        total = len(history)
        churned = sum(1 for row in history if row.get("result", {}).get("prediction") == 1)
        high = sum(1 for row in history if row.get("result", {}).get("risk_level") == "High")
        st.divider()
        st.subheader("Your account overview")
        k1,k2,k3 = st.columns(3)
        k1.metric("Saved predictions", total)
        k2.metric("Predicted churn", churned)
        k3.metric("High-risk customers", high)
        if history:
            latest = history[0].get("result", {})
            st.subheader("Most recent saved prediction")
            a,b,c = st.columns(3)
            a.metric("Churn probability", f"{float(latest.get('churn_probability',0))*100:.2f}%")
            b.metric("Risk level", latest.get("risk_level", "Unknown"))
            c.metric("Outcome", latest.get("result", "Unknown"))
    except requests.exceptions.RequestException:
        st.warning("Could not load account statistics right now.")

elif page == "Predict Churn":
    st.markdown('<div class="section-kicker">Prediction workspace</div>', unsafe_allow_html=True)
    st.title("Predict customer churn")
    st.caption("Enter customer details to generate and save a churn-risk assessment.")
    with st.form("customer_form"):
        st.subheader("👤 Customer profile")
        c1,c2,c3 = st.columns(3)
        with c1:
            gender = st.selectbox("Gender", ["Male", "Female"])
            senior = st.selectbox("Senior citizen", [0,1])
            partner = st.selectbox("Partner", ["Yes","No"])
        with c2:
            dependents = st.selectbox("Dependents", ["Yes","No"])
            tenure = st.number_input("Tenure (months)", 0, 72, 12)
            phone = st.selectbox("Phone service", ["Yes","No"])
        with c3:
            multiple_lines = st.selectbox("Multiple lines", ["No","Yes","No phone service"])
            internet = st.selectbox("Internet service", ["DSL","Fiber optic","No"])
            contract = st.selectbox("Contract", ["Month-to-month","One year","Two year"])
        st.divider(); st.subheader("📡 Services")
        c4,c5,c6 = st.columns(3)
        with c4:
            security = st.selectbox("Online security", ["Yes","No","No internet service"])
            backup = st.selectbox("Online backup", ["Yes","No","No internet service"])
        with c5:
            protection = st.selectbox("Device protection", ["Yes","No","No internet service"])
            support = st.selectbox("Tech support", ["Yes","No","No internet service"])
        with c6:
            tv = st.selectbox("Streaming TV", ["Yes","No","No internet service"])
            movies = st.selectbox("Streaming movies", ["Yes","No","No internet service"])
        st.divider(); st.subheader("💳 Billing information")
        c7,c8,c9 = st.columns(3)
        with c7: paperless = st.selectbox("Paperless billing", ["Yes","No"])
        with c8:
            payment = st.selectbox("Payment method", ["Electronic check","Mailed check","Bank transfer (automatic)","Credit card (automatic)"])
        with c9:
            monthly_charges = st.number_input("Monthly charges ($)", min_value=0.0, value=70.35)
            total_charges = st.number_input("Total charges ($)", min_value=0.0, value=845.50)
        submitted = st.form_submit_button("⚡ Generate churn prediction", use_container_width=True)
    if submitted:
        customer_data = {"gender":gender,"SeniorCitizen":senior,"Partner":partner,"Dependents":dependents,"tenure":tenure,"PhoneService":phone,"MultipleLines":multiple_lines,"InternetService":internet,"OnlineSecurity":security,"OnlineBackup":backup,"DeviceProtection":protection,"TechSupport":support,"StreamingTV":tv,"StreamingMovies":movies,"Contract":contract,"PaperlessBilling":paperless,"PaymentMethod":payment,"MonthlyCharges":monthly_charges,"TotalCharges":total_charges}
        try:
            with st.spinner("Analyzing customer profile and saving result..."):
                response = api_request("POST", "/predict", token=st.session_state["auth_token"], json=customer_data)
            if response.status_code == 200:
                result = response.json()
                st.session_state["latest_prediction"] = result
                st.session_state["latest_customer"] = customer_data
                st.success("Prediction generated and saved to your account history.")
                render_prediction_result(result)
            elif response.status_code == 401:
                st.error("Your session expired. Log out and sign in again.")
            else:
                show_api_error(response, "Prediction")
        except requests.exceptions.Timeout:
            st.error("Prediction request timed out. The free backend may be waking up; try once more.")
        except requests.exceptions.RequestException:
            st.error("Could not connect to the backend. Check the API service and try again.")
    elif st.session_state.get("latest_prediction"):
        st.divider(); st.subheader("Most recent prediction")
        render_prediction_result(st.session_state["latest_prediction"])

elif page == "Prediction History":
    st.markdown('<div class="section-kicker">Your saved analyses</div>', unsafe_allow_html=True)
    st.title("Prediction history")
    st.caption("Only predictions saved under your signed-in account are shown here.")
    if st.button("↻ Refresh history"):
        st.rerun()
    try:
        history = fetch_history()
        if not history:
            st.info("No saved predictions yet. Generate your first prediction from Predict Churn.")
        else:
            st.caption(f"Showing {len(history)} most recent records (maximum 100).")
            for row in history:
                result = row.get("result", {})
                customer = row.get("customer_data", {})
                timestamp = row.get("created_at", "")
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    timestamp_label = dt.astimezone().strftime("%d %b %Y · %I:%M %p")
                except Exception:
                    timestamp_label = timestamp
                label = f"#{row.get('id')} · {result.get('result','Prediction')} · {result.get('risk_level','Unknown')} risk · {timestamp_label}"
                with st.expander(label):
                    x,y,z = st.columns(3)
                    x.metric("Churn probability", f"{float(result.get('churn_probability',0))*100:.2f}%")
                    y.metric("Risk level", result.get("risk_level", "Unknown"))
                    z.metric("Prediction", result.get("result", "Unknown"))
                    st.markdown("**Customer profile**")
                    st.json(customer, expanded=False)
                    st.markdown("**Retention recommendations**")
                    for recommendation in result.get("recommendations", []): st.write(f"• {recommendation}")
                    st.markdown("**Top churn factors**")
                    for factor in result.get("top_churn_factors", []):
                        st.write(f"• {format_feature_name(factor.get('feature',''))}: {factor.get('direction','')} ({float(factor.get('impact',0)):+.4f})")
    except requests.exceptions.RequestException:
        st.error("Unable to load prediction history. Check the backend connection.")

elif page == "AI Insights":
    st.markdown('<div class="section-kicker">Explainability & recommendations</div>', unsafe_allow_html=True)
    st.title("AI insights")
    st.caption("Review the explanation and recommendations from your latest prediction.")
    latest = st.session_state.get("latest_prediction")
    if not latest:
        try:
            history = fetch_history()
            latest = history[0].get("result") if history else None
        except requests.exceptions.RequestException:
            latest = None
    if not latest:
        st.info("No prediction is available yet. Go to Predict Churn and analyze a customer first.")
    else:
        probability = float(latest["churn_probability"]); risk = latest.get("risk_level", "Unknown")
        factors = latest.get("top_churn_factors", []); recommendations = latest.get("recommendations", [])
        c1,c2 = st.columns(2); c1.metric("Churn probability", f"{probability*100:.2f}%"); c2.metric("Current risk level", risk)
        st.divider(); st.subheader("Key factors influencing the prediction")
        if factors:
            max_impact = max((abs(float(f.get("impact",0))) for f in factors), default=0.0)
            for factor in factors:
                impact=float(factor.get("impact",0))
                with st.container(border=True):
                    st.markdown(f"**{format_feature_name(factor['feature'])}**")
                    st.caption(factor.get("direction", "Impact unavailable"))
                    st.metric("SHAP impact", f"{impact:+.4f}")
                    st.progress(abs(impact)/max_impact if max_impact else 0.0)
        else: st.info("No SHAP factors were returned for this prediction.")
        st.divider(); st.subheader("Recommended retention actions")
        for item in recommendations: st.info(f"📌 {item}")
        st.caption("Insights are based on the model response and are not a guarantee of future customer behavior.")

