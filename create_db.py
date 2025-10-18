import sys
from sqlalchemy import create_engine, text

# Configuration to connect to the default 'postgres' database
TEMP_DB_URL = "postgresql+psycopg2://postgres:tiger@127.0.0.1:5432/postgres"
TARGET_DB_NAME = "datasci"

try:
    engine = create_engine(TEMP_DB_URL, isolation_level="AUTOCOMMIT")
    with engine.connect() as connection:
        # Check if the database already exists
        db_exists = connection.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{TARGET_DB_NAME}'")).scalar()
        
        if not db_exists:
            # Create the 'datasci' database
            connection.execute(text(f"CREATE DATABASE {TARGET_DB_NAME};"))
            print(f"Database '{TARGET_DB_NAME}' created successfully. ✅")
        else:
            print(f"Database '{TARGET_DB_NAME}' already exists. Skipping creation. ✅")
except Exception as e:
    print(f"Error connecting to PostgreSQL or creating the database: {e}")
    sys.exit(1)