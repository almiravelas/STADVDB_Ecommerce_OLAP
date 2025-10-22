import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
import time  

@st.cache_data(ttl=600)
def get_product_view_data(_engine: Engine) -> tuple[pd.DataFrame, float]:
    """
    Queries for the detailed Product View.
    Fetches row-level data for price filtering but *omits date join* for performance, as dates are not used in this view.
    """
    if _engine is None:
        return pd.DataFrame(), 0.0

    # --- MODIFICATION: Removed dim_date join, kept row-level data ---
    query = """
        SELECT
            fs.sales_amount AS total_sales, -- Keep alias for view compatibility
            fs.quantity,
            dp.product_name,
            dp.category,
            dp.price
        FROM fact_sales fs
        JOIN dim_product dp ON fs.product_key = dp.product_key
    """
    # --- END MODIFICATION ---
    
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        
        return df, duration
        
    except Exception as e:
        st.error(f"Failed to load product view data: {e}")
        return pd.DataFrame(), 0.0

@st.cache_data(ttl=600)
def get_dashboard_product_data(_engine: Engine) -> tuple[pd.DataFrame, float]:
    """
    Queries for the Dashboard product preview.
    Fetches data pre-aggregated by product and date.
    """
    if _engine is None:
        return pd.DataFrame(), 0.0

    # --- NEW FUNCTION: Pre-aggregates by product and date ---
    query = """
        SELECT
            dp.product_name,
            dp.category,
            dd.year,
            dd.month_name,
            SUM(fs.sales_amount) AS total_sales
        FROM fact_sales fs
        JOIN dim_product dp ON fs.product_key = dp.product_key
        JOIN dim_date dd ON fs.date_key = dd.date_key
        GROUP BY
            dp.product_name,
            dp.category,
            dd.year,
            dd.month_name
    """
    # --- END NEW FUNCTION ---
    
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        
        return df, duration
        
    except Exception as e:
        st.error(f"Failed to load dashboard product data: {e}")
        return pd.DataFrame(), 0.0