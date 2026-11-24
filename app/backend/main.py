import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import bcrypt
import joblib
import numpy as np
import pandas as pd
import shap
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, Integer, String, create_engine, desc
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

# Load .env from project root. On Render, set these as environment variables.
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing. Add it to .env or the hosting environment.")

# SQLAlchemy 2.x with psycopg 3
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    customer_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    result: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True, nullable=False
    )


# Create only the two application tables if they do not already exist.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Customer Churn Prediction API",
    description="AI-powered telecom customer churn prediction, authentication and retention recommendations",
    version="2.0",
)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    # Local-only fallback. Set a unique strong JWT_SECRET_KEY in Render before deployment.
    JWT_SECRET_KEY = "LOCAL-ONLY-CHANGE-THIS-SECRET-BEFORE-DEPLOYMENT-9f7c2a"
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 24
auth_scheme = HTTPBearer(auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    # bcrypt has a 72-byte input limit.
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password must be 72 bytes or fewer")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expires}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(auth_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = int(payload.get("sub", ""))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired login token")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account not found")
    return user


class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=72)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=1, max_length=72)


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
# LOAD EXISTING MODEL + SHAP
# =========================
MODEL_PATH = BASE_DIR / "models" / "churn_model.pkl"
THRESHOLD_PATH = BASE_DIR / "models" / "churn_threshold.pkl"
BACKGROUND_PATH = BASE_DIR / "models" / "shap_background.pkl"

model = joblib.load(MODEL_PATH)
threshold = float(joblib.load(THRESHOLD_PATH))
preprocessor = model.named_steps["preprocessing"]
classifier = model.named_steps["classifier"]
background_data = joblib.load(BACKGROUND_PATH)
background_transformed = preprocessor.transform(background_data)
explainer = shap.LinearExplainer(classifier, background_transformed)
feature_names = preprocessor.get_feature_names_out()


def explain_churn(customer_df: pd.DataFrame):
    transformed_customer = preprocessor.transform(customer_df)
    shap_values = np.asarray(explainer.shap_values(transformed_customer))
    if shap_values.ndim == 3:
        shap_values = shap_values[:, :, -1]
    values = shap_values.reshape(-1)

    effects = []
    for name, value in zip(feature_names, values):
        effects.append({
            "feature": str(name),
            "impact": round(float(value), 4),
            "direction": "Increases churn risk" if value > 0 else "Decreases churn risk",
        })
    effects.sort(key=lambda item: abs(item["impact"]), reverse=True)
    return effects[:5]


def generate_recommendations(customer: CustomerData, probability: float):
    recommendations = []
    if probability >= 0.60:
        recommendations.append(
            "High churn risk: contact the customer personally and offer a targeted retention incentive."
        )
    elif probability >= threshold:
        recommendations.append(
            "Customer is at moderate churn risk. Monitor engagement and consider a personalized offer."
        )
    else:
        recommendations.append("Customer has relatively low churn risk. Continue regular engagement.")

    if customer.Contract == "Month-to-month":
        recommendations.append("Offer an incentive to move the customer to a one-year contract.")
    if customer.MonthlyCharges >= 70:
        recommendations.append("Review pricing and offer a suitable lower-cost plan if appropriate.")
    if customer.TechSupport == "No":
        recommendations.append("Consider offering technical support to improve customer experience.")
    if customer.OnlineSecurity == "No":
        recommendations.append("Consider an online security add-on or bundled service.")
    return recommendations


@app.get("/")
def home():
    return {
        "message": "Customer Churn Prediction API is running",
        "version": "2.0",
        "model_loaded": True,
        "shap_enabled": True,
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": True,
        "shap_enabled": True,
        "threshold": round(threshold, 4),
        "database_configured": True,
    }


@app.post("/auth/signup")
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise HTTPException(status_code=422, detail="Enter a valid email address")

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    user = User(
        name=payload.name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "user": {"id": user.id, "name": user.name, "email": user.email},
    }


@app.post("/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "user": {"id": user.id, "name": user.name, "email": user.email},
    }


@app.get("/auth/me")
def get_me(user: User = Depends(get_current_user)):
    return {"id": user.id, "name": user.name, "email": user.email}


@app.get("/history")
def get_history(
    limit: int = 50,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    limit = max(1, min(limit, 100))
    rows = (
        db.query(PredictionHistory)
        .filter(PredictionHistory.user_id == user.id)
        .order_by(desc(PredictionHistory.created_at))
        .limit(limit)
        .all()
    )
    return [
        {
            "id": row.id,
            "created_at": row.created_at.isoformat(),
            "customer_data": row.customer_data,
            "result": row.result,
        }
        for row in rows
    ]


@app.post("/predict")
def predict_churn(
    customer: CustomerData,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    customer_df = pd.DataFrame([customer.model_dump()])
    probability = float(model.predict_proba(customer_df)[0][1])
    prediction = int(probability >= threshold)

    if probability >= 0.60:
        risk_level = "High"
    elif probability >= threshold:
        risk_level = "Moderate"
    else:
        risk_level = "Low"

    result = {
        "prediction": prediction,
        "result": "Churn" if prediction == 1 else "No Churn",
        "risk_level": risk_level,
        "churn_probability": round(probability, 4),
        "threshold": round(threshold, 4),
        "recommendations": generate_recommendations(customer, probability),
        "top_churn_factors": explain_churn(customer_df),
    }

    history_record = PredictionHistory(
        user_id=user.id,
        customer_data=customer.model_dump(),
        result=result,
    )
    db.add(history_record)
    db.commit()

    return result
