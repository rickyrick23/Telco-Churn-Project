# ChurnGuard Pro: Prescriptive AI for Telecom Retention 🚀

An enterprise-grade, decoupled platform built for predicting high-value customer churn and generating personalized, actionable retention strategies.

Built with love by  Rohit Mukherjee 


## Project Overview: From Prediction to Prescription

This project solves the critical telecom business problem of customer attrition by shifting from simple prediction (identifying who will leave) to **prescriptive analytics** (telling retention agents why they will leave and how to save them).

The application is deployed on a decoupled, two-service architecture (FastAPI and Streamlit) for maximum scalability and performance.

### Key Features and Innovation

| Feature | Technical Implementation | Business Value |
| :--- | :--- | :--- |
| **Prescriptive AI Scripting** | LLM Simulation (GPT/OpenAI) | Generates a multi-paragraph, empathetic email script tailored to the customer's specific risk factors. |
| **Financial Prioritization** | Customer Lifetime Value (CLV) Calculation | Prioritizes intervention efforts by targeting high-risk customers who are also high-value. |
| **Model Transparency (XAI)** | Local Feature Analysis | Displays the Top 3 Drivers (e.g., Network Quality, Contract Risk) for each individual prediction, building trust in the model. |
| **Service Quality (SQ) Integration** | Enhanced ML Features | Incorporates proxies for Call Interruption Rate and Tech Support Incidents to ground predictions in service quality. |
| **Advanced Visuals** | Plotly 3D Surface Plot & Treemaps | Provides interactive visuals that demonstrate the complex interaction of churn drivers. |

-----

## 🏗️ Technical Architecture (MLOps Ready)

The system runs on a robust, decoupled, and container-friendly structure:

1.  **FastAPI Backend:** Loads the ML assets (.pkl files) on startup, connects to PostgreSQL, and exposes secure JSON API endpoints (e.g., /predict\_churn, /metrics).
2.  **Streamlit Frontend:** The user interface layer. It calls the FastAPI API to send data and retrieve predictions/metrics.
3.  **PostgreSQL (Cloud Database):** The persistent, single source of truth for all customer and interaction data.

-----

## 🚀 Quick Start: Running the Project Locally

To run the application, you need two separate terminal windows running simultaneously.

### Prerequisites

1.  Install PostgreSQL and ensure the server is running on port 5432 with user postgres and password tiger.
2.  Install Python Dependencies (from the project root):
    ```bash
    pip install -r requirements.txt
    ```

### Step 1: Database Initialization and Data Loading

The following scripts create the necessary tables and load the data.

```bash
# 1. Create the 'datasci' database (Run once)
python create_db.py

# 2. Load all data into PostgreSQL (Run once)
python load_data.py
```

### Step 2: Build and Save the ML Model

This trains the Random Forest model and saves the assets to the backend/ folder.

```bash
python model_building.py
```

### Step 3: Launch Both Services

Open two separate terminal windows for these commands:

| Terminal 1 (Backend API) | Terminal 2 (Streamlit UI) |
| :--- | :--- |
| **Navigate to Root Directory** | **Navigate to Root Directory** |
| Run the FastAPI server: | Run the Streamlit frontend: |
| `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000` | `streamlit run frontend/app_ui.py` |

Your application will open at http://localhost:8501.

-----

## ☁️ Deployment Note

This project is structured for cloud deployment. To deploy this application publicly, the Cloud Database URL and your OpenAI API Key must be securely set as environment variables (or Streamlit Secrets) in the cloud hosting environment (e.g., Streamlit Community Cloud or AWS).
