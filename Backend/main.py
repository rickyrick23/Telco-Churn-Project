import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from typing import Dict, Any, List

# --- Import Business Logic ---
# NOTE: retention_logic.py is in the parent directory, so we add the parent path temporarily
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from retention_logic import generate_retention_strategy, generate_llm_script_proxy 
sys.path.pop()

# --- Configuration ---
DB_URL = "postgresql+psycopg2://postgres:tiger@127.0.0.1:5432/datasci"
engine = create_engine(DB_URL)

# --- Utility Functions (Model Loading) ---
MODEL = None
SCALER = None
FEATURE_NAMES = None

def load_ml_assets():
    """Load the ML model and scaler from the backend directory."""
    global MODEL, SCALER, FEATURE_NAMES
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, 'churn_model.pkl')
        scaler_path = os.path.join(base_dir, 'scaler.pkl')
        
        MODEL = joblib.load(model_path)
        SCALER = joblib.load(scaler_path)
        FEATURE_NAMES = SCALER.feature_names_in_.tolist()
        print("✅ ML Assets Loaded Successfully by FastAPI.")
    except Exception as e:
        print(f"❌ Error Loading ML Assets: {e}")
        raise RuntimeError("ML assets failed to load.") from e

# --- Pydantic Schema for API Input (Must match Streamlit form data) ---
class PredictionInput(BaseModel):
    tenure: float
    monthly_charges: float
    contract_type: str
    internet_service: str
    payment_method: str
    paperless_billing: str
    call_interrupt_rate: float
    avg_bandwidth_usage: float
    tech_support_incidents: float

# --- FastAPI Application Instance ---
app = FastAPI(title="ChurnGuard Pro API", version="2.0")

# --- Startup Event ---
@app.on_event("startup")
def startup_event():
    load_ml_assets()

# --- API Endpoints ---

# Endpoint 1: Health Check (Model/Server Status)
@app.get("/health")
def health_check():
    if MODEL and SCALER:
        return {"status": "ok", "model_status": "loaded", "feature_count": len(FEATURE_NAMES)}
    raise HTTPException(status_code=503, detail="Service Unavailable: ML assets failed to load.")

# Endpoint 2: Prediction and Strategy Generation
@app.post("/predict_churn")
def predict_churn(data: PredictionInput):
    if not MODEL or not SCALER:
        raise HTTPException(status_code=503, detail="Model not loaded.")
        
    # 1. Prepare Input for Model
    input_features = {
        'tenure': data.tenure, 'monthlycharges': data.monthly_charges,
        'paperlessbilling': 1 if data.paperless_billing == 'Yes' else 0,
        'internetservice_Fiber optic': 1 if data.internet_service == "Fiber optic" else 0,
        'internetservice_No': 1 if data.internet_service == "No" else 0,
        'contract_One year': 1 if data.contract_type == "One year" else 0,
        'contract_Two year': 1 if data.contract_type == "Two year" else 0,
        'paymentmethod_Credit card (automatic)': 1 if data.payment_method == "Credit card (automatic)" else 0,
        'paymentmethod_Electronic check': 1 if data.payment_method == "Electronic check" else 0,
        'paymentmethod_Mailed check': 1 if data.payment_method == "Mailed check" else 0,
        'paymentmethod_Bank transfer (automatic)': 1 if data.payment_method == "Bank transfer (automatic)" else 0,
        'Call_Interruption_Rate': data.call_interrupt_rate,
        'Avg_Bandwidth_Usage': data.avg_bandwidth_usage,
        'Tech_Support_Incidents': data.tech_support_incidents,
    }

    # Create full feature vector using the model's exact feature names
    full_features = {f: input_features.get(f, 0) for f in FEATURE_NAMES}
    input_df = pd.DataFrame([full_features])
    
    # 2. Scale and Predict
    scaled_input = SCALER.transform(input_df)
    churn_probability = MODEL.predict_proba(scaled_input)[:, 1][0]

    # 3. Generate XAI Factors (for output)
    # The XAI factors are generated using the preprocessed (but unscaled) input features
    xai_factors = {
        'Call_Interruption_Rate': data.call_interrupt_rate,
        'contract_Month-to-month': 1 if data.contract_type == "Month-to-month" else 0,
        'monthlycharges': data.monthly_charges,
        'tenure': data.tenure
    }
    
    # 4. Generate Strategy/Script
    strategy = generate_retention_strategy(xai_factors, churn_probability, xai_factors)
    llm_script = generate_llm_script_proxy(churn_probability, xai_factors)

    return {
        "churn_probability": round(churn_probability, 4),
        "xai_factors": xai_factors,
        "strategy": strategy,
        "llm_script": llm_script
    }

# Endpoint 3 (NEW): Get Customer Count
@app.get("/customers/count")
def get_customer_count():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM customers_data"))
            count = result.scalar()
        return {"total_customers": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {e}")

# Endpoint 4 (NEW): Get Interactions Count
@app.get("/interactions/count")
def get_interactions_count():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM interactions_data"))
            count = result.scalar()
        return {"total_interactions": count}
    except Exception:
        return {"total_interactions": 0} # Safe fallback

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)