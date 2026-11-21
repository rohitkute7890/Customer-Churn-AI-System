
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import shap
import numpy as np
from pathlib import Path

app = FastAPI(
    title="Customer Churn Prediction API",
    description="AI-powered telecom customer churn prediction and retention recommendation system",
    version="1.0"
)

# =========================
# PROJECT PATHS
# =========================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "models" / "churn_model.pkl"
THRESHOLD_PATH = BASE_DIR / "models" / "churn_threshold.pkl"
BACKGROUND_PATH = BASE_DIR / "models" / "shap_background.pkl"

# =========================
# LOAD MODEL
# =========================

model = joblib.load(MODEL_PATH)
threshold = float(joblib.load(THRESHOLD_PATH))

# Extract preprocessing and classifier from saved pipeline
preprocessor = model.named_steps["preprocessing"]
classifier = model.named_steps["classifier"]

# Load SHAP background data
background_data = joblib.load(BACKGROUND_PATH)

background_transformed = preprocessor.transform(background_data)

# Initialize SHAP Explainer
explainer = shap.LinearExplainer(
    classifier,
    background_transformed
)

feature_names = preprocessor.get_feature_names_out()

# =========================
# CUSTOMER INPUT SCHEMA
# =========================

class CustomerData(BaseModel):
    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float

# =========================
# SHAP EXPLANATION
# =========================

def explain_churn(customer_df):

    transformed_customer = preprocessor.transform(customer_df)

    shap_values = explainer.shap_values(transformed_customer)

    # Convert SHAP output into a NumPy array
    shap_values = np.asarray(shap_values)

    # Handle different output shapes
    if shap_values.ndim == 3:
        shap_values = shap_values[:, :, -1]

    values = shap_values.reshape(-1)

    feature_effects = []

    for name, value in zip(feature_names, values):

        feature_effects.append({
            "feature": str(name),
            "impact": round(float(value), 4),
            "direction": (
                "Increases churn risk"
                if value > 0
                else "Decreases churn risk"
            )
        })

    # Sort features by absolute SHAP impact
    feature_effects.sort(
        key=lambda item: abs(item["impact"]),
        reverse=True
    )

    return feature_effects[:5]

# =========================
# RETENTION RECOMMENDATION ENGINE
# =========================

def generate_recommendations(customer, probability):

    recommendations = []

    if probability >= 0.60:

        recommendations.append(
            "High churn risk: contact the customer personally "
            "and offer a targeted retention incentive."
        )

    elif probability >= threshold:

        recommendations.append(
            "Customer is at moderate churn risk. "
            "Monitor engagement and consider a personalized offer."
        )

    else:

        recommendations.append(
            "Customer has relatively low churn risk. "
            "Continue regular engagement."
        )

    if customer.Contract == "Month-to-month":

        recommendations.append(
            "Offer an incentive to move the customer to a one-year contract."
        )

    if customer.MonthlyCharges >= 70:

        recommendations.append(
            "Review pricing and offer a suitable lower-cost plan if appropriate."
        )

    if customer.TechSupport == "No":

        recommendations.append(
            "Consider offering technical support to improve customer experience."
        )

    if customer.OnlineSecurity == "No":

        recommendations.append(
            "Consider an online security add-on or bundled service."
        )

    return recommendations

# =========================
# HOME ENDPOINT
# =========================

@app.get("/")
def home():

    return {
        "message": "Customer Churn Prediction API is running",
        "version": "1.0",
        "model_loaded": True,
        "shap_enabled": True
    }

# =========================
# HEALTH CHECK
# =========================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "model_loaded": True,
        "shap_enabled": True,
        "threshold": round(threshold, 4)
    }

# =========================
# CHURN PREDICTION
# =========================

@app.post("/predict")
def predict_churn(customer: CustomerData):

    customer_df = pd.DataFrame([customer.model_dump()])

    # Predict churn probability
    probability = float(
        model.predict_proba(customer_df)[0][1]
    )

    # Apply tuned threshold
    prediction = int(probability >= threshold)

    # Determine risk level
    if probability >= 0.60:
        risk_level = "High"

    elif probability >= threshold:
        risk_level = "Moderate"

    else:
        risk_level = "Low"

    # Generate retention recommendations
    recommendations = generate_recommendations(
        customer,
        probability
    )

    # Generate SHAP explanations
    shap_explanation = explain_churn(customer_df)

    # Return API response
    return {
        "prediction": prediction,
        "result": "Churn" if prediction == 1 else "No Churn",
        "risk_level": risk_level,
        "churn_probability": round(probability, 4),
        "threshold": round(threshold, 4),
        "recommendations": recommendations,
        "top_churn_factors": shap_explanation
    }
