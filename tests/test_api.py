
from fastapi.testclient import TestClient
from app.backend.main import app
from pydantic import ValidationError
import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.backend import main as api

client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["model_loaded"] is True


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_prediction_requires_login():
    response = client.post("/predict", json={})

    assert response.status_code == 401


def test_history_requires_login():
    response = client.get("/history")

    assert response.status_code == 401


def test_me_requires_login():
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_signup_rejects_invalid_email():
    response = client.post(
        "/auth/signup",
        json={
            "name": "Test User",
            "email": "invalid-email",
            "password": "TestPass123"
        }
    )

    assert response.status_code == 422


def test_signup_rejects_short_password():
    response = client.post(
        "/auth/signup",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "123"
        }
    )

    assert response.status_code == 422


def test_login_rejects_invalid_credentials():
    response = client.post(
        "/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "WrongPassword123"
        }
    )

    assert response.status_code == 401

from types import SimpleNamespace
from unittest.mock import MagicMock

from app.backend import main as api


def test_authenticated_prediction():
    fake_db = MagicMock()

    def override_get_db():
        yield fake_db

    api.app.dependency_overrides[api.get_current_user] = (
        lambda: SimpleNamespace(id=999)
    )
    api.app.dependency_overrides[api.get_db] = override_get_db

    customer = {
        "gender": "Female",
        "SeniorCitizen": 0,
        "Partner": "Yes",
        "Dependents": "No",
        "tenure": 1,
        "PhoneService": "No",
        "MultipleLines": "No phone service",
        "InternetService": "DSL",
        "OnlineSecurity": "No",
        "OnlineBackup": "Yes",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 29.85,
        "TotalCharges": 29.85
    }

    try:
        response = TestClient(api.app).post(
            "/predict",
            json=customer
        )

        assert response.status_code == 200

        result = response.json()
        assert result["model_version"] == "churn-model-v1"

        assert 0 <= result["churn_probability"] <= 1
        assert result["risk_level"] in ["Low", "Moderate", "High"]
        assert "top_churn_factors" in result
        assert "recommendations" in result

        fake_db.add.assert_called_once()
        fake_db.commit.assert_called_once()

    finally:
        api.app.dependency_overrides.clear()
def test_prediction_rejects_extra_fields():
    customer = {
        "gender": "Female",
        "SeniorCitizen": 0,
        "Partner": "Yes",
        "Dependents": "No",
        "tenure": 1,
        "PhoneService": "No",
        "MultipleLines": "No phone service",
        "InternetService": "DSL",
        "OnlineSecurity": "No",
        "OnlineBackup": "Yes",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 29.85,
        "TotalCharges": 29.85,
        "unexpected_field": "invalid"
    }

    response = client.post("/predict", json=customer)
    assert response.status_code == 401
def test_customer_data_rejects_invalid_values():
    from app.backend.main import CustomerData

    valid_data = {
        "gender": "Female",
        "SeniorCitizen": 0,
        "Partner": "Yes",
        "Dependents": "No",
        "tenure": 1,
        "PhoneService": "No",
        "MultipleLines": "No phone service",
        "InternetService": "DSL",
        "OnlineSecurity": "No",
        "OnlineBackup": "Yes",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 29.85,
        "TotalCharges": 29.85
    }

    invalid_data = valid_data.copy()
    invalid_data["tenure"] = -1

    with pytest.raises(ValidationError):
        CustomerData.model_validate(invalid_data)
def test_customer_data_rejects_missing_fields():
    from app.backend.main import CustomerData

    with pytest.raises(ValidationError):
        CustomerData.model_validate({
            "gender": "Female"
        })


def test_customer_data_rejects_invalid_category():
    from app.backend.main import CustomerData

    with pytest.raises(ValidationError):
        CustomerData.model_validate({
            "gender": "Other",
            "SeniorCitizen": 0,
            "Partner": "Yes",
            "Dependents": "No",
            "tenure": 1,
            "PhoneService": "No",
            "MultipleLines": "No phone service",
            "InternetService": "DSL",
            "OnlineSecurity": "No",
            "OnlineBackup": "Yes",
            "DeviceProtection": "No",
            "TechSupport": "No",
            "StreamingTV": "No",
            "StreamingMovies": "No",
            "Contract": "Month-to-month",
            "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 29.85,
            "TotalCharges": 29.85
        })
def test_readiness_endpoint():
    response = client.get('/ready')

    assert response.status_code == 200
    result = response.json()
    assert result['status'] == 'ready'
    assert result['model_loaded'] is True
    assert result['shap_enabled'] is True
    assert result['model_version'] == 'churn-model-v1'

def test_prediction_database_failure():
    customer = api.CustomerData(
        gender="Female",
        SeniorCitizen=0,
        Partner="Yes",
        Dependents="No",
        tenure=1,
        PhoneService="No",
        MultipleLines="No phone service",
        InternetService="DSL",
        OnlineSecurity="No",
        OnlineBackup="Yes",
        DeviceProtection="No",
        TechSupport="No",
        StreamingTV="No",
        StreamingMovies="No",
        Contract="Month-to-month",
        PaperlessBilling="Yes",
        PaymentMethod="Electronic check",
        MonthlyCharges=29.85,
        TotalCharges=29.85
    )

    fake_db = MagicMock()
    fake_db.commit.side_effect = SQLAlchemyError("Database unavailable")

    user = SimpleNamespace(id=999)

    with pytest.raises(HTTPException) as exc:
        api.predict_churn(customer, user, fake_db)

    assert exc.value.status_code == 500
    fake_db.add.assert_called_once()
    fake_db.rollback.assert_called_once()
def test_request_body_size_limit():
    large_payload = 'x' * (17 * 1024)

    response = client.post(
        '/predict',
        content=large_payload,
        headers={'Content-Type': 'application/json'}
    )

    assert response.status_code == 413

def test_prediction_inference_failure(monkeypatch):
    customer = api.CustomerData(
        gender="Female",
        SeniorCitizen=0,
        Partner="Yes",
        Dependents="No",
        tenure=1,
        PhoneService="No",
        MultipleLines="No phone service",
        InternetService="DSL",
        OnlineSecurity="No",
        OnlineBackup="Yes",
        DeviceProtection="No",
        TechSupport="No",
        StreamingTV="No",
        StreamingMovies="No",
        Contract="Month-to-month",
        PaperlessBilling="Yes",
        PaymentMethod="Electronic check",
        MonthlyCharges=29.85,
        TotalCharges=29.85
    )

    def failing_prediction(data):
        raise RuntimeError("Simulated model failure")

    monkeypatch.setattr(api.model, "predict_proba", failing_prediction)

    fake_db = MagicMock()
    user = SimpleNamespace(id=999)

    with pytest.raises(HTTPException) as exc:
        api.predict_churn(customer, user, fake_db)

    assert exc.value.status_code == 500
    assert exc.value.detail == "The prediction could not be completed."
    fake_db.add.assert_not_called()
    fake_db.commit.assert_not_called()