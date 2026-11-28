# Customer Churn Prediction AI System

An end-to-end customer churn prediction application for telecom
customers. The system combines a trained machine-learning model, a
FastAPI backend, a Streamlit interface, authenticated user accounts,
prediction history, and SHAP-based explanations.

## Project Overview

The application estimates the likelihood that a telecom customer will
churn and presents a risk assessment with supporting factors and
retention recommendations.

### Key Features

-   Customer churn prediction through a Streamlit interface
-   Logistic Regression model with a tuned classification threshold
-   Low-, moderate-, and high-risk presentation
-   SHAP-based explanation of influential customer features
-   Retention recommendations
-   FastAPI REST API
-   Signup, login, and authenticated user profile
-   User-specific prediction history
-   PostgreSQL persistence
-   Request validation and controlled API error handling
-   Docker Compose setup for the backend and frontend
-   Health and readiness endpoints

## Technology Stack

  Area               Technologies
  ------------------ ------------------------------------
  Language           Python 3.13
  Machine learning   scikit-learn, NumPy, pandas, SciPy
  Explainable AI     SHAP
  Backend            FastAPI, Uvicorn, Pydantic
  Frontend           Streamlit
  Database           PostgreSQL, SQLAlchemy, psycopg
  Authentication     JWT, python-jose, bcrypt
  HTTP client        Requests
  Containerization   Docker, Docker Compose

## Project Structure

``` text
Customer-Churn-AI-System/
├── app/
│   ├── backend/
│   │   ├── main.py
│   │   └── main_backup.py
│   └── frontend/
│       └── streamlit_app.py
├── data/
│   └── WA_Fn-UseC_-Telco-Customer-Churn.csv
├── models/
│   ├── churn_model.pkl
│   ├── churn_threshold.pkl
│   └── shap_background.pkl
├── notebooks/
├── reports/
├── tests/
│   └── test_api.py
├── .dockerignore
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── requirements-docker.txt
```

The `.env` file is intentionally not included in this structure because
it contains local configuration and secrets. Do not commit it to source
control.

## Machine Learning

The application uses a trained Logistic Regression classifier. The
prediction threshold is loaded from `models/churn_threshold.pkl` rather
than relying on the default 0.5 cutoff.

Recorded validation threshold-tuning results:

  Metric                    Value
  ---------------------- --------
  Selected threshold       0.2755
  Validation precision      0.537
  Validation recall         0.776
  Validation F1-score       0.635

These are validation results from the threshold-selection experiment,
not a guarantee of production performance. Re-evaluate the model on
fresh, representative data before operational use.

SHAP is used to explain influential features for an individual
prediction. The application also uses the saved background data in
`models/shap_background.pkl`.

## Backend API

The FastAPI application is defined in `app/backend/main.py`.

  -----------------------------------------------------------------------
  Method                  Endpoint                Purpose
  ----------------------- ----------------------- -----------------------
  GET                     `/`                     Root endpoint

  GET                     `/health`               Health check

  GET                     `/ready`                Readiness check

  POST                    `/auth/signup`          Create an account

  POST                    `/auth/login`           Authenticate and obtain
                                                  a token

  GET                     `/auth/me`              Get the authenticated
                                                  user's profile

  GET                     `/history`              Retrieve the
                                                  authenticated user's
                                                  prediction history

  POST                    `/predict`              Predict customer churn
  -----------------------------------------------------------------------

Interactive API documentation is available at `/docs` while the backend
is running.

## Configuration

Create a `.env` file in the project root. Supply your own values; never
publish real credentials.

``` env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE
JWT_SECRET_KEY=REPLACE_WITH_A_LONG_RANDOM_SECRET
```

The backend reads these values from the environment. The Docker Compose
configuration passes `.env` to the backend container. Keep `.env` out of
Git and do not paste its contents into issue reports or screenshots.

## Run Locally Without Docker

Use Python 3.13 and run these commands from the project root.

### 1. Create and activate a virtual environment

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

``` powershell
pip install -r requirements.txt
```

### 3. Start the backend

``` powershell
uvicorn app.backend.main:app --host 0.0.0.0 --port 8000
```

### 4. Start the frontend in a second terminal

``` powershell
.\.venv\Scripts\Activate.ps1
$env:API_BASE_URL = "http://127.0.0.1:8000"
streamlit run app/frontend/streamlit_app.py --server.port 8501
```

Open the frontend at `http://localhost:8501`. The API documentation is
at `http://localhost:8000/docs`.

## Run With Docker Compose

Ensure Docker Desktop is running and the root `.env` file is configured.

### Build the images

``` powershell
docker compose build
```

### Start the services

``` powershell
docker compose up -d
```

### Check container and health status

``` powershell
docker compose ps
```

Both services are configured with health checks. The backend readiness
endpoint is `/ready`; the Streamlit health endpoint is
`/_stcore/health`.

### View logs

``` powershell
docker compose logs --tail=50
```

### Stop the services

``` powershell
docker compose down
```

### Local service addresses

  Service              Address
  -------------------- ------------------------------
  Streamlit frontend   http://localhost:8501
  FastAPI backend      http://localhost:8000
  Swagger API docs     http://localhost:8000/docs
  Backend health       http://localhost:8000/health
  Backend readiness    http://localhost:8000/ready

## Testing

The API test suite is located at `tests/test_api.py`.

Run it with:

``` powershell
python -m pytest tests/test_api.py -v
```

The latest recorded test run in the development workflow completed with
**17 passed**. Run the suite again after code or dependency changes and
update this result if it changes.

## Security Notes

-   Never commit `.env`, database credentials, JWT secrets, or access
    tokens.
-   Use a unique, randomly generated `JWT_SECRET_KEY` for each
    environment.
-   Use HTTPS and secure secret management for public deployments.
-   Do not expose internal exception details or secrets in API responses
    and logs.
-   Restrict database network access and use least-privilege
    credentials.
-   Rotate any credential that has been accidentally exposed.

## Limitations and Further Improvements

Potential next steps include automated model monitoring, drift
detection, scheduled retraining, stronger deployment observability,
CI/CD, and broader integration tests. These should be treated as future
work unless they have been implemented and verified in this repository.

## License

Add the license and ownership terms applicable to this project before
publishing or redistributing it.
