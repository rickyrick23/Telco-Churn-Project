import pandas as pd
from sqlalchemy import create_engine
import os
import sys

# --- Configuration ---
DB_URL = "postgresql+psycopg2://postgres:tiger@localhost:5432/datasci"
DB_NAME = "datasci"

# Determine the correct path to the data files
# We assume the data folder is 'data/raw/' relative to the script's execution path
CUSTOMERS_CSV_PATH = "data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv"
INTERACTIONS_CSV_PATH = "data/raw/customer_interactions.csv"

# --- Helper Functions for Preprocessing ---
def load_and_preprocess_customers(csv_path: str) -> pd.DataFrame:
    """Loads and preprocesses the customer data before loading to SQL."""
    df = pd.read_csv(csv_path, low_memory=False)
    
    # 1. Rename columns to be database-friendly (snake_case)
    df.columns = [col.lower().replace('id', '_id').replace(' ', '_') for col in df.columns]
    df = df.rename(columns={'seniorcitizen': 'senior_citizen', 'totalcharges': 'total_charges', 
                            'monthlycharges': 'monthly_charges', 'phoneservice': 'phone_service'})

    # 2. Basic Cleaning (TotalCharges)
    df['total_charges'] = df['total_charges'].replace(' ', '0')
    df['total_charges'] = pd.to_numeric(df['total_charges'], errors='coerce').fillna(0)
    
    # 3. Handle Boolean columns
    bool_cols = ['churn', 'partner', 'dependents', 'senior_citizen', 'paperlessbilling']
    for col in bool_cols:
        if col in df.columns:
             # Map YES/NO strings to the boolean representation the database will use
             df[col] = df[col].astype(str).str.lower().map({'yes': True, 'no': False, 'true': True, 'false': False}).fillna(False)
             
    return df

def load_and_preprocess_interactions(csv_path: str) -> pd.DataFrame:
    """Loads and preprocesses the interaction data."""
    df = pd.read_csv(csv_path, low_memory=False)
    df.columns = [col.lower().replace('id', '_id').replace(' ', '_') for col in df.columns]
    return df

# --- Main Loading Logic ---
def main():
    try:
        engine = create_engine(f"postgresql+psycopg2://postgres:tiger@localhost:5432/{DB_NAME}")
        
        # 1. Load Customers Data
        customers_df = load_and_preprocess_customers(CUSTOMERS_CSV_PATH)
        customers_df.to_sql('customers_data', engine, if_exists='replace', index=False, method='multi')
        print("Customer data loaded successfully into 'customers_data'. (7043 records) ✅")
        
        # 2. Load Interactions Data
        interactions_df = load_and_preprocess_interactions(INTERACTIONS_CSV_PATH)
        interactions_df.to_sql('interactions_data', engine, if_exists='replace', index=False, method='multi')
        print(f"Interaction data loaded successfully into 'interactions_data'. ({len(interactions_df)} records) ✅")
        
        print("\n🎉 All raw data loaded successfully into PostgreSQL.")
        
    except FileNotFoundError as e:
        print(f"Error: Required CSV file not found. Please check your data/raw folder. Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nFATAL ERROR during database load: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()