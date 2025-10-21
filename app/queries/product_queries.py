import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
import time  

@st.cache_data(ttl=600)
def get_product_data(_engine: Engine) -> tuple[pd.DataFrame, float]:
    """
    Queries the data warehouse to get sales data joined with product dimension details.
    ...
    """
    if _engine is None:
        return pd.DataFrame(), 0.0  # Return empty DataFrame and duration

    query = """
        SELECT
            fs.sales_amount AS total_sales,
            fs.quantity,
            dp.product_name,
            dp.category,
            dp.price,
            dd.year,
            dd.month_name
        FROM fact_sales fs
        JOIN dim_product dp ON fs.product_key = dp.product_key
        JOIN dim_date dd ON fs.date_key = dd.date_key
    """
    
    try:
        start_time = time.perf_counter()  # Start timer
        df = pd.read_sql(query, _engine)   # Execute query
        duration = time.perf_counter() - start_time  # Calculate duration
        
        return df, duration  # Return DataFrame and duration
        
    except Exception as e:
        st.error(f"Failed to load product data: {e}")
        return pd.DataFrame(), 0.0