import os
import pandas as pd
from sqlalchemy import create_engine

def extract_from_db(query: str) -> pd.DataFrame:
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    source_db_name = os.getenv("SOURCE_DB_NAME")
    
    if not all([db_user, db_password, db_host, source_db_name]):
        print("Error: Database environment variables are not fully set.")
        return None

    try:
        connection_url = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{source_db_name}"
        engine = create_engine(connection_url)
        
        # extract data
        print(f"Executing query on source DB '{source_db_name}'...")
        df = pd.read_sql(query, engine)
        print("Data extracted successfully.")
        return df

    except Exception as e:
        print(f"Failed to connect or fetch data from source. Error: {e}")
        return None