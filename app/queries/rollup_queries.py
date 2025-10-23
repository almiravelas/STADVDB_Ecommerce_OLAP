"""
Roll-up Operations - Aggregation to higher level of granularity
"""
import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
import time

AOV_EXPR = "SUM(fs.sales_amount)/NULLIF(COUNT(DISTINCT fs.order_number),0)"


@st.cache_data(ttl=300)  # Cache for 5 minutes
def rollup_sales_by_year(_engine: Engine) -> tuple[pd.DataFrame, float, str, tuple | None]:
    """Roll up sales data to year level (highest granularity)"""
    if _engine is None:
        return pd.DataFrame(), 0.0, "", None
    
    query = f"""
        SELECT 
            dd.year,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            {AOV_EXPR} AS avg_order_value
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        GROUP BY dd.year
        ORDER BY dd.year;
    """
    params = None
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        return df, duration, query, params
    except Exception as e:
        st.error(f"Failed to execute roll-up query: {e}")
        return pd.DataFrame(), 0.0, query, params


@st.cache_data(ttl=300)  # Cache for 5 minutes
def rollup_sales_by_quarter(_engine: Engine) -> tuple[pd.DataFrame, float, str, tuple | None]:
    """Roll up sales data to quarter level"""
    if _engine is None:
        return pd.DataFrame(), 0.0, "", None
    
    query = f"""
        SELECT 
            dd.year,
            dd.quarter,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            {AOV_EXPR} AS avg_order_value
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        GROUP BY dd.year, dd.quarter
        ORDER BY dd.year, dd.quarter;
    """
    params = None
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        return df, duration, query, params
    except Exception as e:
        st.error(f"Failed to execute roll-up query: {e}")
        return pd.DataFrame(), 0.0, query, params


@st.cache_data(ttl=300)  # Cache for 5 minutes
def rollup_sales_by_category(_engine: Engine) -> tuple[pd.DataFrame, float, str, tuple | None]:
    """Roll up sales data by product category"""
    if _engine is None:
        return pd.DataFrame(), 0.0, "", None
    
    query = f"""
        SELECT 
            dp.category,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            {AOV_EXPR} AS avg_order_value,
            COUNT(DISTINCT dp.product_key) AS product_count
        FROM fact_sales fs
        JOIN dim_product dp ON fs.product_key = dp.product_key
        GROUP BY dp.category
        ORDER BY total_sales DESC;
    """
    params = None
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        return df, duration, query, params
    except Exception as e:
        st.error(f"Failed to execute roll-up query: {e}")
        return pd.DataFrame(), 0.0, query, params


@st.cache_data(ttl=300)  # Cache for 5 minutes
def rollup_sales_by_courier(_engine: Engine) -> tuple[pd.DataFrame, float, str, tuple | None]:
    """Roll up sales by courier (rider dimension)"""
    if _engine is None:
        return pd.DataFrame(), 0.0, "", None
    
    query = f"""
        SELECT 
            dr.courier_name,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            {AOV_EXPR} AS avg_order_value,
            COUNT(DISTINCT fs.rider_key) AS rider_count
        FROM fact_sales fs
        JOIN dim_rider dr ON fs.rider_key = dr.rider_key
        GROUP BY dr.courier_name
        ORDER BY total_sales DESC;
    """
    # Note: Added rider_count to your original query based on your rollup_view.py
    params = None
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        return df, duration, query, params
    except Exception as e:
        st.error(f"Failed to execute roll-up query: {e}")
        return pd.DataFrame(), 0.0, query, params


@st.cache_data(ttl=300)  # Cache for 5 minutes
def rollup_sales_by_region(_engine: Engine) -> tuple[pd.DataFrame, float, str, tuple | None]:
    """Roll up sales data by region/continent"""
    if _engine is None:
        return pd.DataFrame(), 0.0, "", None
    
    query = f"""
        SELECT 
            du.continent,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            {AOV_EXPR} AS avg_order_value,
            COUNT(DISTINCT du.country) AS country_count
        FROM fact_sales fs
        JOIN dim_user du ON fs.customer_key = du.user_key
        GROUP BY du.continent
        ORDER BY total_sales DESC;
    """
    params = None
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        return df, duration, query, params
    except Exception as e:
        st.error(f"Failed to execute roll-up query: {e}")
        return pd.DataFrame(), 0.0, query, params