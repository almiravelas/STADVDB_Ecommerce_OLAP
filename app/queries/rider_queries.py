import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
import time  # Import the time module

@st.cache_data(ttl=600)
def get_sales_with_rider_details(_engine: Engine) -> tuple[pd.DataFrame, float]:
    """
    Fetches detailed, row-level sales data joined with ALL
    rider and date attributes for the detailed Rider Analytics view.
    
    (NO CHANGE: This view is *meant* to be detailed, so raw data is correct.)
    """
    if _engine is None:
        return pd.DataFrame(), 0.0

    query = """
        SELECT
            fs.order_number,
            fs.quantity,
            fs.unit_price,
            fs.sales_amount,
            dr.rider_key, -- Use key for accurate distinct counts
            dr.rider_name,
            dr.vehicleType,
            dr.gender,
            dr.age,
            dr.courier_name,
            dd.year, 
            dd.month_name 
        FROM fact_sales fs
        JOIN dim_rider dr ON fs.rider_key = dr.rider_key
        JOIN dim_date dd ON fs.date_key = dd.date_key; 
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        return df, duration
        
    except Exception as e:
        st.error(f"Failed to load detailed rider data: {e}")
        return pd.DataFrame(), 0.0

@st.cache_data(ttl=600)
def get_sales_for_dashboard(_engine: Engine) -> tuple[pd.DataFrame, float]:
    """
    Fetches data pre-aggregated at the ORDER level,
    which is the grain needed for dashboard metrics and charts.
    
    Returns a tuple: (pd.DataFrame, float) where float is the
    query execution time in seconds.
    """
    if _engine is None:
        return pd.DataFrame(), 0.0

    # --- MODIFICATION: Query is now pre-aggregated ---
    # We group by the order and its associated rider/date dimensions.
    # We SUM() the sales_amount for each order.
    # This massively reduces row count if fact_sales is at the line-item level.
    query = """
        SELECT
            fs.order_number,
            dr.rider_key, 
            dr.rider_name, 
            dr.courier_name,
            dd.year, 
            dd.month_name,
            SUM(fs.sales_amount) AS sales_amount
        FROM fact_sales fs
        JOIN dim_rider dr ON fs.rider_key = dr.rider_key
        JOIN dim_date dd ON fs.date_key = dd.date_key
        GROUP BY
            fs.order_number,
            dr.rider_key,
            dr.rider_name,
            dr.courier_name,
            dd.year, 
            dd.month_name;
    """
    # --- END MODIFICATION ---
    
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        return df, duration
        
    except Exception as e:
        st.error(f"Failed to load dashboard sales data: {e}")
        return pd.DataFrame(), 0.0