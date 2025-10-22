"""
Pivot Queries - Server-side conditional aggregation friendly
"""
import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
import time


@st.cache_data(ttl=600)
def pivot_category_by_month(_engine: Engine) -> tuple[pd.DataFrame, float]:
    """Pivot: Categories as rows, months as columns"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    query = """
        SELECT 
            dp.category,
            dd.year,
            dd.month,
            dd.month_name,
            SUM(fs.sales_amount) AS total_sales
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        JOIN dim_product dp ON fs.product_key = dp.product_key
        GROUP BY dp.category, dd.year, dd.month, dd.month_name
        ORDER BY dp.category, dd.year, dd.month;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute pivot query: {e}")
        return pd.DataFrame(), 0.0


@st.cache_data(ttl=600)
def pivot_city_by_category(_engine: Engine) -> tuple[pd.DataFrame, float]:
    """Pivot: Cities vs Categories"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    query = """
        SELECT 
            du.city,
            dp.category,
            SUM(fs.sales_amount) AS total_sales,
            COUNT(DISTINCT fs.order_number) AS total_orders
        FROM fact_sales fs
        JOIN dim_user du ON fs.customer_key = du.user_key
        JOIN dim_product dp ON fs.product_key = dp.product_key
        GROUP BY du.city, dp.category
        ORDER BY du.city, dp.category;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute pivot query: {e}")
        return pd.DataFrame(), 0.0


@st.cache_data(ttl=600)
def pivot_year_by_quarter(_engine: Engine) -> tuple[pd.DataFrame, float]:
    """Pivot: Year vs Quarter for high-level trend"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    query = """
        SELECT 
            dd.year,
            dd.quarter,
            SUM(fs.sales_amount) AS total_sales,
            COUNT(DISTINCT fs.order_number) AS total_orders
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        GROUP BY dd.year, dd.quarter
        ORDER BY dd.year, dd.quarter;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute pivot query: {e}")
        return pd.DataFrame(), 0.0
