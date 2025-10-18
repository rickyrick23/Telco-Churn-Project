import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier # Using Random Forest for high accuracy
from sklearn.preprocessing import StandardScaler
import joblib
import os
import sys

# --- Configuration ---
DB_URL = "postgresql+psycopg2://postgres:tiger@localhost:5432/datasci"
engine = create_engine(DB_URL)

def run_model_pipeline():
    try:
        # Step 1: Fetch Data from Database
        query = "SELECT * FROM customers_data"
        customers_df = pd.read_sql_query(query, engine)
        
    except Exception as e:
        print(f"Error fetching data from the database: {e}")
        sys.exit(1)

    # --- Step 2: Data Preprocessing for the Model ---
    
    # 2.1 Final Cleaning and Mapping
    if 'index' in customers_df.columns:
        customers_df = customers_df.drop(columns=['index'])
        
    # Standardize column naming convention
    customers_df.columns = customers_df.columns.str.lower()
    customers_df = customers_df.rename(columns={'customer_id': 'customer_id'}) 

    # Convert the 'churn' column to the numerical target (1 for True, 0 for False)
    customers_df['churn'] = customers_df['churn'].astype(int)

    # Convert boolean columns from DB (True/False) to 1/0 for ML model
    bool_to_int_cols = ['senior_citizen', 'partner', 'dependents', 'paperlessbilling']
    for col in bool_to_int_cols:
         if col in customers_df.columns:
             customers_df[col] = customers_df[col].astype(int)

    # 2.2 Handle remaining categorical columns (One-Hot Encoding)
    categorical_cols = customers_df.select_dtypes(include=['object']).columns
    if 'customer_id' in categorical_cols:
        categorical_cols = categorical_cols.drop('customer_id')

    customers_df = pd.get_dummies(customers_df, columns=categorical_cols, drop_first=True)

    # 2.3 Define X (features) and y (target)
    y = customers_df['churn']
    X = customers_df.drop(columns=['customer_id', 'churn'])
    
    # 2.4 Add new Service Quality (SQ) placeholder columns and fill them with 0
    # The model expects these features, even if they aren't in the original dataset
    sq_features = ['call_interruption_rate', 'avg_bandwidth_usage', 'tech_support_incidents']
    for feature in sq_features:
        if feature not in X.columns:
            X[feature] = 0

    # 2.5 Ensure feature alignment before splitting
    X = X.reindex(columns=sorted(X.columns), fill_value=0) # Sorts columns alphabetically

    # 2.6 Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # --- Step 3: Feature Scaling ---
    # Scaling is still a best practice for consistency, even if RF doesn't strictly need it
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # --- Step 4: Train and Save the Model ---
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42, class_weight='balanced')
    model.fit(X_train_scaled, y_train)

    # Save the trained assets to the 'backend' folder
    joblib.dump(model, 'backend/churn_model.pkl')
    joblib.dump(scaler, 'backend/scaler.pkl')

    print("\n✅ Random Forest Model (backend/churn_model.pkl) and Scaler saved successfully.")
    
if __name__ == "__main__":
    run_model_pipeline()