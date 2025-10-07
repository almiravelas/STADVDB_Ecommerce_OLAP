import os
import pandas as pd
from sqlalchemy import create_engine

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
            
            df.to_sql(
                table_name,
                connection,
                if_exists='replace',
                index=False,
                # added this to process the data in batches of 50,000 rows (WIP)
                chunksize=50000 
            )
            
            transaction.commit()
            print(f"Data loaded into '{table_name}' and transaction committed.")

        except Exception as e:
            print(f"Failed to load data to {warehouse_db_name}. Error: {e}")
            transaction.rollback()
            print("Transaction has been rolled back.")