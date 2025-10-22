"""
Slice Operations - Fix one dimension value
"""
import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
import time


@st.cache_data(ttl=600)
def slice_by_year(_engine: Engine, year: int) -> tuple[pd.DataFrame, float]:
    """Slice data for a specific year across all dimensions"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    query = """
        SELECT 
            dd.month_name,
            dp.category,
            du.city AS user_city,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            COUNT(DISTINCT fs.order_number) AS total_orders
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        JOIN dim_product dp ON fs.product_key = dp.product_key
        JOIN dim_user du ON fs.customer_key = du.user_key
        WHERE dd.year = %s
        GROUP BY dd.month_name, dp.category, du.city
        ORDER BY total_sales DESC;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=(year,))
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute slice query: {e}")
        return pd.DataFrame(), 0.0


@st.cache_data(ttl=600)
def slice_by_category(_engine: Engine, category: str) -> tuple[pd.DataFrame, float]:
    """Slice data for a specific product category"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    query = """
        SELECT 
            dd.year,
            dd.month_name,
            dp.product_name,
            du.city AS user_city,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            COUNT(DISTINCT fs.order_number) AS total_orders
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        JOIN dim_product dp ON fs.product_key = dp.product_key
        JOIN dim_user du ON fs.customer_key = du.user_key
        WHERE dp.category = %s
        GROUP BY dd.year, dd.month_name, dp.product_name, du.city
        ORDER BY total_sales DESC;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=(category,))
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute slice query: {e}")
        return pd.DataFrame(), 0.0


@st.cache_data(ttl=600)
def slice_by_city(_engine: Engine, city: str) -> tuple[pd.DataFrame, float]:
    """Slice data for a specific user city"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    query = """
        SELECT 
            dd.year,
            dd.month_name,
            dp.category,
            dp.product_name,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            COUNT(DISTINCT fs.order_number) AS total_orders
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        JOIN dim_product dp ON fs.product_key = dp.product_key
        JOIN dim_user du ON fs.customer_key = du.user_key
        WHERE du.city = %s
        GROUP BY dd.year, dd.month_name, dp.category, dp.product_name
        ORDER BY total_sales DESC;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=(city,))
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute slice query: {e}")
        return pd.DataFrame(), 0.0


@st.cache_data(ttl=600)
def slice_by_courier(_engine: Engine, courier: str) -> tuple[pd.DataFrame, float]:
    """Slice data for a specific courier"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    AOV_EXPR = "SUM(fs.sales_amount)/NULLIF(COUNT(DISTINCT fs.order_number),0)"
    
    query = f"""
        SELECT 
            dr.courier_name,
            dd.year,
            dd.month_name,
            dp.category,
            du.city,
            dr.vehicleType,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            {AOV_EXPR} AS avg_order_value
        FROM fact_sales fs
        JOIN dim_rider dr ON fs.rider_key = dr.rider_key
        JOIN dim_date dd ON fs.date_key = dd.date_key
        JOIN dim_product dp ON fs.product_key = dp.product_key
        JOIN dim_user du ON fs.customer_key = du.user_key
        WHERE dr.courier_name = %s
        GROUP BY dr.courier_name, dd.year, dd.month_name, dp.category, du.city, dr.vehicleType
        ORDER BY dd.year, dd.month_name, total_sales DESC;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=(courier,))
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute courier slice query: {e}")
        return pd.DataFrame(), 0.0
