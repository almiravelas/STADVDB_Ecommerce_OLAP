import os
import pandas as pd
from sqlalchemy import create_engine, text  # <-- 1. IMPORT 'text'

def load_to_warehouse(df: pd.DataFrame, table_name: str):
    if df is None:
        print(f"No data to load for table '{table_name}'. Skipping.")
        return

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    warehouse_db_name = os.getenv("WAREHOUSE_DB_NAME")
    
    if not all([db_user, db_password, db_host, warehouse_db_name]):
        print("Error: Warehouse environment variables are not fully set.")
        return

    connection_url = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{warehouse_db_name}"
    engine = create_engine(connection_url)

    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            print(f"Loading data into table '{table_name}' in warehouse '{warehouse_db_name}'...")
            
            # --- 2. ADD THIS LOGIC BLOCK ---
            # This logic preserves your partitions for fact_sales
            if table_name == 'fact_sales':
                print(f"Truncating '{table_name}' to preserve partitions...")
                connection.execute(text(f"TRUNCATE TABLE {table_name}"))
                if_exists_strategy = 'append'
            else:
                # Dimensions can be fully replaced
                if_exists_strategy = 'replace'
            # --- END OF BLOCK ---

            df.to_sql(
                table_name,
                connection,
                if_exists=if_exists_strategy,  # <-- 3. USE THE VARIABLE
                index=False,
                chunksize=50000 
            )
            
            transaction.commit()
            print(f"Data loaded into '{table_name}' and transaction committed.")

        except Exception as e:
            print(f"Failed to load data to {warehouse_db_name}. Error: {e}")
            transaction.rollback()
            print("Transaction has been rolled back.")