r"""
Utility to load two CSV files into an existing PostgreSQL database named 'datasci'.

Tables expected to exist already:
  - customers_data(customer_id PRIMARY KEY, ...)
  - interactions_data(id BIGSERIAL, customer_id REFERENCES customers_data(customer_id), interaction_text)

Usage (PowerShell):
  # Load both
  python load_to_datasci.py --customers_csv "C:\Users\arjun\datascience\customers.csv" --interactions_csv "C:\Users\arjun\datascience\interactions.csv" --ask

  # Load only customers
  python load_to_datasci.py --customers_csv "C:\Users\arjun\datascience\customers.csv" --skip_interactions --ask

You can also pass connection details via flags or environment variables:
  Flags: --database_url OR --host --port --user --password --database
  Env:   DATABASE_URL or PGUSER, PGPASSWORD, PGHOST, PGPORT, PGDATABASE (defaults to datasci)

If --ask is provided or values are missing, the script will interactively prompt you.
"""

import os
import argparse
import getpass
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.dialects.postgresql import BOOLEAN, INTEGER, TEXT, NUMERIC


def build_database_url(args) -> str:
    if getattr(args, "database_url", None):
        return args.database_url

    env_user = os.getenv("PGUSER", "postgres")
    env_password = os.getenv("PGPASSWORD", "tiger")
    env_host = os.getenv("PGHOST", "localhost")
    env_port = os.getenv("PGPORT", "5432")
    env_db = os.getenv("PGDATABASE", "datasci")

    user = args.user or env_user if hasattr(args, "user") else env_user
    host = args.host or env_host if hasattr(args, "host") else env_host
    port = args.port or env_port if hasattr(args, "port") else env_port
    database = args.database or env_db if hasattr(args, "database") else env_db
    password = args.password if hasattr(args, "password") and args.password is not None else env_password

    if hasattr(args, "ask") and args.ask:
        user_in = input(f"PostgreSQL user [{user}]: ").strip()
        if user_in:
            user = user_in
        host_in = input(f"Host [{host}]: ").strip()
        if host_in:
            host = host_in
        port_in = input(f"Port [{port}]: ").strip()
        if port_in:
            port = port_in
        db_in = input(f"Database [{database}]: ").strip()
        if db_in:
            database = db_in
        pwd_in = getpass.getpass("Password (leave blank to keep current): ")
        if pwd_in != "":
            password = pwd_in

    if user is None or user == "":
        user = input("PostgreSQL user: ").strip() or "postgres"
    if host is None or host == "":
        host = input("Host: ").strip() or "localhost"
    if port is None or port == "":
        port = input("Port: ").strip() or "5432"
    if database is None or database == "":
        database = input("Database: ").strip() or "datasci"
    if password is None:
        password = getpass.getpass("Password: ")

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=user or None,
        password=password or None,
        host=host,
        port=int(port),
        database=database,
    )
    return str(url)


def normalize_yes_no_to_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin(["yes", "y", "true", "1", "t"])


def load_customers_csv(engine, customers_csv_path: str) -> None:
    df = pd.read_csv(customers_csv_path, encoding="utf-8-sig", low_memory=False)

    rename_map = {
        "customerID": "customer_id",
        "gender": "gender",
        "SeniorCitizen": "senior_citizen",
        "Partner": "partner",
        "Dependents": "dependents",
        "tenure": "tenure",
        "PhoneService": "phone_service",
        "MultipleLines": "multiple_lines",
        "InternetService": "internet_service",
        "OnlineSecurity": "online_security",
        "OnlineBackup": "online_backup",
        "DeviceProtection": "device_protection",
        "TechSupport": "tech_support",
        "StreamingTV": "streaming_tv",
        "StreamingMovies": "streaming_movies",
        "Contract": "contract",
        "PaperlessBilling": "paperless_billing",
        "PaymentMethod": "payment_method",
        "MonthlyCharges": "monthly_charges",
        "TotalCharges": "total_charges",
        "Churn": "churn",
    }
    df = df.rename(columns=rename_map)

    if "senior_citizen" in df.columns:
        df["senior_citizen"] = pd.to_numeric(df["senior_citizen"], errors="coerce").fillna(0).astype(int).astype(bool)

    for col in ["partner", "dependents", "paperless_billing", "churn"]:
        if col in df.columns:
            df[col] = normalize_yes_no_to_bool(df[col])

    if "monthly_charges" in df.columns:
        df["monthly_charges"] = pd.to_numeric(df["monthly_charges"], errors="coerce")
    if "total_charges" in df.columns:
        df["total_charges"] = pd.to_numeric(df["total_charges"], errors="coerce")
    if "tenure" in df.columns:
        df["tenure"] = pd.to_numeric(df["tenure"], errors="coerce").astype("Int64")

    ordered_columns = [
        "customer_id",
        "gender",
        "senior_citizen",
        "partner",
        "dependents",
        "tenure",
        "phone_service",
        "multiple_lines",
        "internet_service",
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies",
        "contract",
        "paperless_billing",
        "payment_method",
        "monthly_charges",
        "total_charges",
        "churn",
    ]
    existing_cols = [c for c in ordered_columns if c in df.columns]
    df = df[existing_cols]

    dtype_map = {
        "customer_id": TEXT(),
        "gender": TEXT(),
        "senior_citizen": BOOLEAN(),
        "partner": BOOLEAN(),
        "dependents": BOOLEAN(),
        "tenure": INTEGER(),
        "phone_service": TEXT(),
        "multiple_lines": TEXT(),
        "internet_service": TEXT(),
        "online_security": TEXT(),
        "online_backup": TEXT(),
        "device_protection": TEXT(),
        "tech_support": TEXT(),
        "streaming_tv": TEXT(),
        "streaming_movies": TEXT(),
        "contract": TEXT(),
        "paperless_billing": BOOLEAN(),
        "payment_method": TEXT(),
        "monthly_charges": NUMERIC(10, 2),
        "total_charges": NUMERIC(12, 2),
        "churn": BOOLEAN(),
    }

    # Upsert customers via staging table to avoid duplicate PK errors
    staging_table = "customers_data_staging"
    df.to_sql(
        staging_table,
        engine,
        if_exists="replace",
        index=False,
        dtype={k: v for k, v in dtype_map.items() if k in df.columns},
        method="multi",
        chunksize=5000,
    )

    column_names = df.columns.tolist()
    columns_csv = ", ".join(column_names)
    insert_sql = f"""
        INSERT INTO customers_data ({columns_csv})
        SELECT {columns_csv}
        FROM {staging_table}
        ON CONFLICT (customer_id) DO NOTHING
    """
    with engine.begin() as conn:
        conn.execute(text(insert_sql))
        conn.execute(text(f"DROP TABLE IF EXISTS {staging_table}"))


def _fetch_existing_customer_ids(engine) -> set:
    existing_ids: set = set()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT customer_id FROM customers_data"))
        existing_ids = {row[0] for row in result if row[0] is not None}
    return existing_ids


def _create_placeholder_customers(engine, customer_ids: list[str]) -> int:
    if not customer_ids:
        return 0
    # Insert minimal rows for missing customers; ignore duplicates
    params = [{"cid": cid} for cid in customer_ids]
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO customers_data (customer_id)
                VALUES (:cid)
                ON CONFLICT (customer_id) DO NOTHING
                """
            ),
            params,
        )
    return len(customer_ids)


def load_interactions_csv(engine, interactions_csv_path: str, create_missing_customers: bool = False) -> None:
    df = pd.read_csv(interactions_csv_path, encoding="utf-8-sig", low_memory=False)

    # Normalize potential header variants
    # Expecting at least: customerID, interaction_text
    rename_map = {
        "customerID": "customer_id",
        "CustomerID": "customer_id",
        "customer_id": "customer_id",
        "interaction_text": "interaction_text",
        "InteractionText": "interaction_text",
    }
    df = df.rename(columns=rename_map)

    keep_cols = ["customer_id", "interaction_text"]
    existing_cols = [c for c in keep_cols if c in df.columns]
    df = df[existing_cols]

    # Enforce FK behavior: ensure customer_id exists, optionally create placeholders
    if "customer_id" in df.columns:
        df["customer_id"] = df["customer_id"].astype(str).str.strip()
        unique_ids = set(df["customer_id"].dropna().unique().tolist())
        existing_ids = _fetch_existing_customer_ids(engine)
        missing_ids = sorted(list(unique_ids - existing_ids))

        if missing_ids:
            if create_missing_customers:
                _create_placeholder_customers(engine, missing_ids)
                # refresh existing set
                existing_ids = existing_ids.union(set(missing_ids))
                print(f"Created {len(missing_ids)} placeholder customers to satisfy FK.")
            else:
                print(f"Skipping {len(missing_ids)} interactions with unknown customers (use --create_missing_customers to auto-create).")
        # Filter to only those with existing customers
        df = df[df["customer_id"].isin(existing_ids)]

    dtype_map = {
        "customer_id": TEXT(),
        "interaction_text": TEXT(),
    }

    df.to_sql(
        "interactions_data",
        engine,
        if_exists="append",
        index=False,
        dtype=dtype_map,
        method="multi",
        chunksize=5000,
    )


def main():
    parser = argparse.ArgumentParser(description="Load customers and optional interactions CSVs into the datasci database")
    parser.add_argument("--customers_csv", required=True, help="Path to the structured customers CSV")
    parser.add_argument("--interactions_csv", required=False, help="Path to the interactions CSV (optional)")
    parser.add_argument("--skip_interactions", action="store_true", help="Skip loading interactions even if provided")
    parser.add_argument("--create_missing_customers", action="store_true", help="Auto-create placeholder customers for interactions referencing unknown customer_ids")
    # Connection options
    parser.add_argument("--database_url", help="Full SQLAlchemy DB URL (e.g. postgresql+psycopg2://user:pass@host:5432/datasci)")
    parser.add_argument("--host", help="PostgreSQL host")
    parser.add_argument("--port", help="PostgreSQL port")
    parser.add_argument("--user", help="PostgreSQL user")
    parser.add_argument("--password", help="PostgreSQL password")
    parser.add_argument("--database", help="Database name (default datasci)")
    parser.add_argument("--ask", action="store_true", help="Interactively prompt for connection details")
    args = parser.parse_args()

    engine = create_engine(build_database_url(args), pool_pre_ping=True)

    # Load customers first to satisfy foreign key constraint
    load_customers_csv(engine, args.customers_csv)

    # Load interactions if provided and not skipped
    if args.interactions_csv and not args.skip_interactions:
        load_interactions_csv(engine, args.interactions_csv, create_missing_customers=args.create_missing_customers)
    else:
        print("Interactions loading skipped (no path provided or --skip_interactions set).")


if __name__ == "__main__":
    main()


