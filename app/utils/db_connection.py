import os
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

@st.cache_resource
def get_warehouse_engine():
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("WAREHOUSE_DB_NAME")

    if not all([db_user, db_password, db_host, db_name]):
        st.error("Missing environment variables for DB connection.")
        return None

    try:
        connection_url = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}"
        engine = create_engine(connection_url)
        print("Successfully connected to data warehouse.")
        return engine
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None
