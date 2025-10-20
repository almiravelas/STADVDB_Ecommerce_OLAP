import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
import time  # <-- Import time module

@st.cache_data(ttl=600)
def get_product_data(_engine: Engine) -> tuple[pd.DataFrame, float]: # <-- Update return type hint
    """
    Queries the data warehouse to get sales data joined with product dimension details.
    The results are cached for performance.
    
    Returns a tuple: (pd.DataFrame, float) where float is the
    query execution time in seconds.
    """
    #
    # Return an empty DataFrame if no database connection is provided
    if _engine is None:
        return pd.DataFrame(), 0.0  # <-- Return tuple

    # SQL query to join the sales fact table with the product dimension table
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
        JOIN dim_date dd ON fs.date_key = dd.date_key;
    """
    try:
        # --- MODIFICATION: Start timer ---
        start_time = time.perf_counter() # <-- Add timer start
        
        # Execute the query and load the result into a pandas DataFrame
        df = pd.read_sql(query, _engine)
        
        # --- MODIFICATION: End timer and calculate duration ---
        end_time = time.perf_counter()   # <-- Add timer end
        duration = end_time - start_time   # <-- Calculate duration
        
        return df, duration  # <-- Return tuple
        
    except Exception as e:
        # Display an error in the Streamlit app if the query fails
        st.error(f"Failed to load product data: {e}")
        return pd.DataFrame(), 0.0  # <-- Return tuple on error