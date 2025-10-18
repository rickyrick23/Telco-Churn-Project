import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from textblob import TextBlob
import numpy as np
import os

# --- CONFIGURATION ---
API_BASE_URL = "http://127.0.0.1:8000"

# --- STREAMLIT CONFIGURATION ---
st.set_page_config(page_title="ChurnGuard Pro - Final Enterprise Portal", layout="wide")

# --- DATA FETCHING FUNCTIONS (Remains the same) ---
@st.cache_data(ttl=300)
def fetch_api_data(endpoint):
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.ConnectionError:
        return None

@st.cache_data(ttl=300)
def get_full_data_from_db():
    try:
        from sqlalchemy import create_engine
        DB_URL = "postgresql+psycopg2://postgres:tiger@127.0.0.1:5432/datasci"
        engine = create_engine(DB_URL)
        df = pd.read_sql_query("SELECT * FROM customers_data", engine)
        df['churn'] = df['churn'].astype(str).str.lower().map({'t': 'Churned', 'f': 'Active'}).fillna('Active')
        df.columns = df.columns.str.lower()
        df = df.rename(columns={'monthlycharges': 'monthly_charges', 'totalcharges': 'total_charges'})
        return df
    except Exception as e:
        return pd.DataFrame()


# --- BUSINESS LOGIC FUNCTIONS ---
def calculate_clv(monthly_charges, churn_probability):
    churn_prob = max(churn_probability, 0.01) 
    average_lifetime_months = 1 / churn_prob
    gross_margin = 0.30
    clv_value = monthly_charges * gross_margin * average_lifetime_months
    return int(clv_value)

def get_xai_factors(input_data_df, feature_names):
    xai_factors = {}
    if input_data_df.get('Call_Interruption_Rate', 0) > 10:
         xai_factors["Network Quality"] = "High Interruptions"
    if input_data_df['contract_Month-to-month'].iloc[0] == 1:
         xai_factors["Contract Risk"] = "Month-to-month"
    if input_data_df['monthlycharges'].iloc[0] > 90:
         xai_factors["Financial Factor"] = "High Monthly Charge"
    if input_data_df['tenure'].iloc[0] < 12:
         xai_factors["Customer Loyalty"] = "New Customer (Low Tenure)"
    return dict(list(xai_factors.items())[:3])

def generate_llm_script_mock(churn_probability: float, xai_factors: dict, sentiment: str) -> str:
    """
    Mocks the final, clean multi-paragraph LLM script output.
    """
    if churn_probability < 0.5:
        return "Customer is low-risk. No proactive intervention script required."
    
    primary_issue = list(xai_factors.values())[0] if xai_factors else "general dissatisfaction"
    risk_level = "CRITICAL" if churn_probability > 0.8 else "HIGH"
    
    if sentiment == 'Negative':
        tone = "We sincerely apologize for the frustration evident in your recent feedback and want to act immediately."
    elif sentiment == 'Positive':
        tone = "We appreciate your positive feedback and are proactively offering a loyalty reward."
    else:
        tone = "We are reaching out proactively to ensure your account remains stable."

    script = f"""
Subject: Urgent Check-in: Addressing Your {primary_issue} Service Concerns

Dear Valued Customer,

{tone} Our system flags your account as {risk_level} RISK ({churn_probability:.2%}) due to factors like your {primary_issue}. We want to ensure you stay satisfied.

To make things right, we are immediately offering a complimentary Premium Support Tier upgrade for the next six months and a $50 service credit to offset any inconvenience. If the issue is related to Network Quality, we will dispatch a senior technician for a priority inspection at your home within 24 hours, free of charge.

Please reply to this email or call our dedicated retention line (555-SAVE) to accept this offer and ensure your service issues are permanently resolved.

Sincerely,
The ChurnGuard Retention Team
"""
    return script.strip()


# --- UI RENDERER FUNCTIONS ---

def render_visualization_dashboard():
    """Renders all advanced visualizations (TAB 2)."""
    st.header("Advanced Visual Analysis")
    st.markdown("Dive deep into customer segment risk and feature impact.")

    customer_data = get_full_data_from_db()

    if not customer_data.empty:
        customer_data['churn_numeric'] = customer_data['churn'].astype(str).map({'Churned': 1, 'Active': 0}).fillna(0)
        
        col_graph1, col_graph2 = st.columns(2)
        
        # 1. Treemap of Segment Risk
        segment_df = customer_data.groupby(['contract', 'internetservice'])['churn_numeric'].agg(['mean', 'count']).reset_index(names=['contract', 'internetservice'])
        segment_df['churn_rate_pct'] = segment_df['mean'] * 100
        fig_treemap = px.treemap(
            segment_df, path=[px.Constant("All Segments"), 'contract', 'internetservice'],
            values='count', color='churn_rate_pct', color_continuous_scale='RdYlGn_r', 
            title="1. Customer Segmentation by Churn Rate (Treemap)"
        )
        col_graph1.plotly_chart(fig_treemap, use_container_width=True)
        
        # 2. 3D Churn Driver Surface Plot
        churners_df = customer_data[customer_data['churn'] == 'Churned'].copy()
        churners_df['total_charges'] = pd.to_numeric(churners_df['total_charges'], errors='coerce').fillna(0)
        
        fig_3d = go.Figure(data=[go.Scatter3d(
            x=churners_df['tenure'], y=churners_df['monthly_charges'], z=churners_df['total_charges'],
            mode='markers',
            marker=dict(size=3, color=churners_df['churn_numeric'], colorscale='Viridis', opacity=0.8)
        )])
        
        fig_3d.update_layout(scene = dict(xaxis_title='Tenure (Months)', yaxis_title='Monthly Charges ($)', zaxis_title='Total Charges ($)'), height=600, margin=dict(l=0, r=0, b=0, t=0), title='2. 3D Churn Driver Surface (Tenure, Charges, Total)')
        col_graph2.plotly_chart(fig_3d, use_container_width=True)

def render_batch_ranking_dashboard():
    """Renders the batch prediction and ranking (TAB 3)."""
    st.header("Batch Prediction & High-Risk Ranking")
    st.markdown("Identify the top customers most likely to churn for immediate action.")

    if st.button("Generate Top 50 Riskiest Customers"):
        st.info("Simulating batch prediction results...")
        
        mock_df = pd.DataFrame({
            'Customer ID': ['5575-GNVDE', '7590-VHVEG', '9305-CDWPC', '1234-ABCD'],
            'Churn Probability': ['95.12%', '88.45%', '75.31%', '99.00%'],
            'Contract': ['Month-to-month', 'Month-to-month', 'One year', 'Month-to-month'],
            'Monthly Charges': [105.00, 95.00, 75.00, 110.00],
            'CLV Rank': ['#1', '#2', '#3', '#4']
        })
        st.dataframe(mock_df, use_container_width=True)

    # --- Customer Service Incident Log (For Context) ---
    st.markdown("---")
    st.subheader("Customer Service Incident & Billing Snapshot")
    st.markdown("*Note: In a real system, this data would be fetched from the PostgreSQL Interactions table.*")
    
    incidents_data = {
        'Date': ['2025-09-01', '2025-08-15', '2025-07-20', '2025-06-05'],
        'Customer ID': ['5575-GNVDE', '9305-CDWPC', '5575-GNVDE', '7590-VHVEG'],
        'Issue Type': ['Network Outage', 'Unpaid Bill (15 days overdue)', 'Slow Speed', 'Dropped Calls'],
        'Status': ['Resolved - Comp Sent', 'PENDING ACTION', 'Resolved', 'PENDING ACTION'],
        'Customer Feedback': ['Negative', 'Negative', 'Neutral', 'Negative']
    }
    incidents_df = pd.DataFrame(incidents_data)
    
    st.dataframe(incidents_df, hide_index=True, use_container_width=True)


# --------------------------------------------------------------------------
# 4. MAIN APP EXECUTION FLOW
# --------------------------------------------------------------------------

# 1. SIDEBAR AND CONFIGURATION
st.sidebar.title("LLM Configuration")
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="Needed for generating custom retention scripts.")

st.sidebar.title("App Status")
try:
    health_status = requests.get(f"{API_BASE_URL}/health").json()
    st.sidebar.success(f"✅ API Status: {health_status['status'].upper()} (Model Loaded)")
except:
    st.sidebar.error("❌ API Connection Failed. Please ensure 'backend/main.py' is running on port 8000.")


# --- MAIN DASHBOARD LAYOUT ---
st.title("ChurnGuard Pro - Final Enterprise App")
st.markdown("A highly valuable, production-ready solution leveraging FastAPI and PostgreSQL.")

# 2. METRICS OVERVIEW
metrics_col = st.columns(3)
cust_data = fetch_api_data("customers/count")
int_data = fetch_api_data("interactions/count")

customer_count = cust_data.get('total_customers', 'Error') if cust_data else 'API Down'
interactions_count = int_data.get('total_interactions', 'Error') if int_data else 'API Down'

metrics_col[0].metric("Total Customers", customer_count)
metrics_col[1].metric("Total Interactions", interactions_count)
metrics_col[2].metric("API Health", "ONLINE" if customer_count != 'Server Down' else "OFFLINE")

st.markdown("---")


# 3. TABBED INTERFACE
tab1, tab2, tab3 = st.tabs(["🎯 Prediction Console", "📊 Advanced Visuals", "📑 Batch Reports"])


# --------------------------------------------------------------------------
# TAB 1: PREDICTION CONSOLE (Risk Scoring)
# --------------------------------------------------------------------------
with tab1:
    # --- Calling the functions to render the content ---
    # NOTE: The UI structure inside this tab is defined below
    
    st.header("1. Sentiment Analysis (Input Layer)")
    
    # Sentiment Analysis Form
    with st.form("sentiment_form"):
        st.markdown("**Check the customer's emotional state before prediction.**")
        feedback_text = st.text_area("Enter Customer's Recent Feedback:", "I am very upset with the recent service outage.")
        analyze_button = st.form_submit_button("Check Sentiment Score")
        
        if 'current_sentiment' not in st.session_state:
            st.session_state.current_sentiment = 'Neutral'
            st.session_state.sentiment_score = 0.0

        if analyze_button:
            sentiment_score = TextBlob(feedback_text).sentiment.polarity
            if sentiment_score > 0.1:
                st.session_state.current_sentiment = 'Positive'
                st.success(f"Sentiment: **Positive** (Score: {sentiment_score:.2f})")
            elif sentiment_score < -0.1:
                st.session_state.current_sentiment = 'Negative'
                st.error(f"Sentiment: **Negative** (Score: {sentiment_score:.2f})")
            else:
                st.session_state.current_sentiment = 'Neutral'
                st.info(f"Sentiment: **Neutral** (Score: {sentiment_score:.2f})")
            st.session_state.sentiment_score = sentiment_score
        else:
            st.info(f"Current Sentiment in use: **{st.session_state.current_sentiment}** (Score: {st.session_state.sentiment_score:.2f})")

    st.markdown("---")
    st.header("2. Churn Prediction & Strategy")

    with st.form("churn_prediction_form"):
        st.subheader("Customer Metrics")
        
        col_input1, col_input2, col_input3 = st.columns(3)
        tenure = col_input1.number_input("Tenure (months)", min_value=0, max_value=120, value=12)
        monthly_charges = col_input2.number_input("Monthly Charges", min_value=0.0, step=0.01, value=65.50)
        contract_type = col_input3.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])

        st.subheader("Service Quality (SQ) Metrics")
        
        col_sq1, col_sq2, col_sq3 = st.columns(3)
        call_interrupt_rate = col_sq1.slider("Call Interruption Rate (%)", 0, 30, 5)
        avg_bandwidth_usage = col_sq2.number_input("Avg Bandwidth (Mbps)", min_value=0.0, step=0.1, value=10.5)
        tech_support_incidents = col_sq3.slider("Tech Support Incidents (Last 3 Mo)", 0, 10, 1)

        st.subheader("Service/Payment Details")
        col_input4, col_input5, col_input6 = st.columns(3)
        internet_service = col_input4.selectbox("Internet Service", ["Fiber optic", "DSL", "No"])
        payment_method = col_input5.selectbox("Payment Method", ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"])
        paperless_billing = col_input6.selectbox("Paperless Billing", ["Yes", "No"])

        submit_button = st.form_submit_button("Predict Churn Risk & Generate Script")

        if submit_button:
            # 1. Prepare Payload
            payload = {
                "tenure": float(tenure), "monthly_charges": float(monthly_charges), "contract_type": contract_type, 
                "internet_service": internet_service, "payment_method": payment_method, "paperless_billing": paperless_billing,
                "call_interrupt_rate": float(call_interrupt_rate), "avg_bandwidth_usage": float(avg_bandwidth_usage),
                "tech_support_incidents": float(tech_support_incidents)
            }

            # 2. Call API for Prediction
            try:
                response = requests.post(f"{API_BASE_URL}/predict_churn", json=payload)
                
                if response.status_code != 200:
                    st.error(f"Prediction API Error. Status: {response.status_code}. Detail: {response.text}")
                else:
                    result = response.json()
                    churn_probability = result['churn_probability']
                    xai_factors_dict = result['xai_factors']
                    
                    # 3. Generate LLM Script (Local Mock)
                    clv = calculate_clv(monthly_charges, churn_probability)
                    llm_script = generate_llm_script_mock(churn_probability, xai_factors_dict, st.session_state.current_sentiment)

                    # 4. Display Results
                    st.subheader("3. Actionable Results: Risk & Financial Value")
                    
                    col_res1, col_res2 = st.columns([1, 2])
                    
                    col_res1.metric("Predicted Churn Risk", f"{churn_probability:.2%}", delta=f"CLV: ${clv:,}", delta_color="off")
                    
                    col_res2.markdown("**Top Churn Drivers (Explainable AI):**")
                    for key, value in xai_factors_dict.items():
                        col_res2.markdown(f"- **{key}:** {value}")
                    
                    st.subheader("4. AI-Generated Intervention Script")
                    st.code(llm_script)

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the FastAPI prediction service. Please ensure the backend is running.")


# --------------------------------------------------------------------------
# TAB 2: ADVANCED VISUALS (Content called here)
# --------------------------------------------------------------------------
with tab2:
    render_visualization_dashboard()


# --------------------------------------------------------------------------
# TAB 3: BATCH REPORTS (Content called here)
# --------------------------------------------------------------------------
with tab3:
    render_batch_ranking_dashboard()