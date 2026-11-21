
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(
    page_title="Customer Churn AI",
    page_icon="📊",
    layout="wide"
)

# =========================
# HEADER
# =========================

st.title("📊 Customer Churn Prediction")
st.caption("AI-powered telecom customer retention analysis")

st.divider()

# =========================
# CUSTOMER INPUT FORM
# =========================

with st.form("customer_form"):

    st.subheader("👤 Customer Profile")

    c1, c2, c3 = st.columns(3)

    with c1:
        gender = st.selectbox("Gender", ["Male", "Female"])
        senior = st.selectbox("Senior Citizen", [0, 1])
        partner = st.selectbox("Partner", ["Yes", "No"])

    with c2:
        dependents = st.selectbox("Dependents", ["Yes", "No"])
        tenure = st.number_input("Tenure (months)", 0, 72, 12)
        phone = st.selectbox("Phone Service", ["Yes", "No"])

    with c3:
        multiple_lines = st.selectbox(
            "Multiple Lines",
            ["No", "Yes", "No phone service"]
        )

        internet = st.selectbox(
            "Internet Service",
            ["DSL", "Fiber optic", "No"]
        )

        contract = st.selectbox(
            "Contract",
            ["Month-to-month", "One year", "Two year"]
        )

    st.divider()
    st.subheader("📡 Services")

    c4, c5, c6 = st.columns(3)

    with c4:
        security = st.selectbox(
            "Online Security",
            ["Yes", "No", "No internet service"]
        )

        backup = st.selectbox(
            "Online Backup",
            ["Yes", "No", "No internet service"]
        )

    with c5:
        protection = st.selectbox(
            "Device Protection",
            ["Yes", "No", "No internet service"]
        )

        support = st.selectbox(
            "Tech Support",
            ["Yes", "No", "No internet service"]
        )

    with c6:
        tv = st.selectbox(
            "Streaming TV",
            ["Yes", "No", "No internet service"]
        )

        movies = st.selectbox(
            "Streaming Movies",
            ["Yes", "No", "No internet service"]
        )

    st.divider()
    st.subheader("💳 Billing Information")

    c7, c8, c9 = st.columns(3)

    with c7:
        paperless = st.selectbox(
            "Paperless Billing",
            ["Yes", "No"]
        )

    with c8:
        payment = st.selectbox(
            "Payment Method",
            [
                "Electronic check",
                "Mailed check",
                "Bank transfer (automatic)",
                "Credit card (automatic)"
            ]
        )

    with c9:
        monthly_charges = st.number_input(
            "Monthly Charges ($)",
            min_value=0.0,
            value=70.35
        )

        total_charges = st.number_input(
            "Total Charges ($)",
            min_value=0.0,
            value=845.50
        )

    submitted = st.form_submit_button(
        "🔍 Predict Customer Churn",
        use_container_width=True
    )

# =========================
# FEATURE NAME FORMATTER
# =========================

def format_feature_name(name):

    name = name.replace("num__", "")
    name = name.replace("cat__", "")

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
        "gender": "Gender"
    }

    # Identify categorical features and their values
    for original, readable in mappings.items():

        if name.startswith(original + "_"):
            value = name[len(original) + 1:]
            value = value.replace("_", " ")

            return f"{readable}: {value.title()}"

        if name == original:
            return readable

    name = name.replace("_", " ")
    return name.title()


# =========================
# PREDICTION
# =========================

if submitted:

    customer_data = {
        "gender": gender,
        "SeniorCitizen": senior,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": tenure,
        "PhoneService": phone,
        "MultipleLines": multiple_lines,
        "InternetService": internet,
        "OnlineSecurity": security,
        "OnlineBackup": backup,
        "DeviceProtection": protection,
        "TechSupport": support,
        "StreamingTV": tv,
        "StreamingMovies": movies,
        "Contract": contract,
        "PaperlessBilling": paperless,
        "PaymentMethod": payment,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges
    }

    try:

        response = requests.post(
            API_URL,
            json=customer_data,
            timeout=10
        )

        if response.status_code == 200:

            result = response.json()

            churn_probability = result["churn_probability"]
            prediction = result["prediction"]
            risk_level = result.get("risk_level", "Unknown")
            threshold = result["threshold"]
            recommendations = result.get("recommendations", [])

            # =========================
            # PREDICTION RESULT
            # =========================

            st.divider()
            st.subheader("📈 Prediction Result")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Churn Probability",
                    f"{churn_probability * 100:.2f}%"
                )

            with col2:
                st.metric(
                    "Risk Level",
                    risk_level
                )

            with col3:
                st.metric(
                    "Prediction",
                    "Churn" if prediction == 1 else "No Churn"
                )

            if risk_level == "High":
                st.error("⚠️ Customer has high churn risk.")

            elif risk_level == "Moderate":
                st.warning("⚠️ Customer has moderate churn risk.")

            else:
                st.success("✅ Customer has low churn risk.")

            st.progress(
                min(max(float(churn_probability), 0.0), 1.0)
            )

            st.caption(
                f"Decision threshold used: {threshold:.4f}"
            )

            # =========================
            # RETENTION RECOMMENDATIONS
            # =========================

            st.divider()
            st.subheader("💡 Retention Recommendations")

            if recommendations:

                for recommendation in recommendations:
                    st.info(f"📌 {recommendation}")

            else:
                st.write("No recommendations available.")

            # =========================
            # SHAP EXPLANATION
            # =========================

            st.divider()
            st.subheader("🔍 Why did the model make this prediction?")

            st.caption(
                "These factors show which customer attributes influenced "
                "the churn prediction and in which direction."
            )

            factors = result.get("top_churn_factors", [])

            if factors:

                max_impact = max(
                    abs(float(factor["impact"]))
                    for factor in factors
                )

                for factor in factors:

                    feature = format_feature_name(
                        factor["feature"]
                    )

                    impact = float(factor["impact"])
                    direction = factor["direction"]

                    normalized_impact = (
                        abs(impact) / max_impact
                        if max_impact > 0
                        else 0.0
                    )

                    with st.container(border=True):

                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.markdown(f"**{feature}**")

                        with col2:
                            st.metric(
                                "SHAP Impact",
                                f"{impact:+.4f}"
                            )

                        if impact > 0:

                            st.error(
                                f"🔴 {direction}"
                            )

                        elif impact < 0:

                            st.success(
                                f"🟢 {direction}"
                            )

                        else:

                            st.info(
                                "⚪ No directional impact"
                            )

                        st.progress(
                            min(
                                max(normalized_impact, 0.0),
                                1.0
                            )
                        )

            else:

                st.info(
                    "No SHAP explanation available for this prediction."
                )

        else:

            st.error(
                f"API Error ({response.status_code}): {response.text}"
            )

    except requests.exceptions.ConnectionError:

        st.error(
            "Backend is not running. Start FastAPI before making predictions."
        )

    except requests.exceptions.Timeout:

        st.error(
            "The prediction request timed out. Please try again."
        )

    except Exception as e:

        st.error(f"Unexpected error: {e}")
