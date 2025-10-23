"""
Slice Operations - Fix one dimension value
"""
import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
import time


@st.cache_data(ttl=300)  # Cache for 5 minutes
def slice_by_year(_engine: Engine, year: int) -> tuple[pd.DataFrame, float, str, tuple | None]:
    """Slice data for a specific year across all dimensions"""
    if _engine is None:
        return pd.DataFrame(), 0.0, "", None
    
    query = """
        SELECT 
            dd.year,
            dd.month_name,
            dp.category,
            du.city,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            COUNT(fs.order_number) AS total_orders
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        JOIN dim_product dp ON fs.product_key = dp.product_key
        JOIN dim_user du ON fs.customer_key = du.user_key
        WHERE dd.year = %s
        GROUP BY dd.year, dd.month_name, dp.category, du.city
        ORDER BY total_sales DESC;
    """
    params = (year,)
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=params)
        duration = time.perf_counter() - start_time
        return df, duration, query, params
    except Exception as e:
        st.error(f"Failed to execute slice query: {e}")
        return pd.DataFrame(), 0.0, query, params


@st.cache_data(ttl=300)  # Cache for 5 minutes
def slice_by_category(_engine: Engine, category: str) -> tuple[pd.DataFrame, float, str, tuple | None]:
    """Slice data for a specific product category"""
    if _engine is None:
        return pd.DataFrame(), 0.0, "", None
    
    query = """
        SELECT 
            dd.year,
            dd.month_name,
            dp.category,
            dp.product_name,
            du.city,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            COUNT(fs.order_number) AS total_orders
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        JOIN dim_product dp ON fs.product_key = dp.product_key
        JOIN dim_user du ON fs.customer_key = du.user_key
        WHERE dp.category = %s
        GROUP BY dd.year, dd.month_name, dp.category, dp.product_name, du.city
        ORDER BY total_sales DESC;
    """
    params = (category,)
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=params)
        duration = time.perf_counter() - start_time
        return df, duration, query, params
    except Exception as e:
        st.error(f"Failed to execute slice query: {e}")
        return pd.DataFrame(), 0.0, query, params


@st.cache_data(ttl=300)  # Cache for 5 minutes
def slice_by_city(_engine: Engine, city: str) -> tuple[pd.DataFrame, float, str, tuple | None]:
    """Slice data for a specific user city"""
    if _engine is None:
        return pd.DataFrame(), 0.0, "", None
    
    query = """
        SELECT 
            dd.year,
            dd.month_name,
            dp.category,
            dp.product_name,
            du.city,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            COUNT(fs.order_number) AS total_orders
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        JOIN dim_product dp ON fs.product_key = dp.product_key
        JOIN dim_user du ON fs.customer_key = du.user_key
        WHERE du.city = %s
        GROUP BY dd.year, dd.month_name, dp.category, dp.product_name, du.city
        ORDER BY total_sales DESC;
    """
    params = (city,)
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=params)
        duration = time.perf_counter() - start_time
        return df, duration, query, params
    except Exception as e:
        st.error(f"Failed to execute slice query: {e}")
        return pd.DataFrame(), 0.0, query, params


@st.cache_data(ttl=300)  # Cache for 5 minutes
def slice_by_courier(_engine: Engine, courier: str) -> tuple[pd.DataFrame, float, str, tuple | None]:
    """Slice data for a specific courier"""
    if _engine is None:
        return pd.DataFrame(), 0.0, "", None
    
    AOV_EXPR = "SUM(fs.sales_amount)/NULLIF(COUNT(fs.order_number),0)"
    
    query = f"""
        SELECT 
            dr.courier_name,
            dd.year,
            dd.month_name,
            dp.category,
            du.city,
            dr.vehicleType,
            COUNT(fs.order_number) AS total_orders,
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
    params = (courier,)
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=params)
        duration = time.perf_counter() - start_time
        return df, duration, query, params
    except Exception as e:
        st.error(f"Failed to execute courier slice query: {e}")
        return pd.DataFrame(), 0.0, query, params


@st.cache_data(ttl=300)  # Cache for 5 minutes
def slice_by_month(_engine: Engine, year: int, month: int) -> tuple[pd.DataFrame, float, str, tuple | None]:
    """Slice data for a specific year and month"""
    if _engine is None:
        return pd.DataFrame(), 0.0, "", None
    
    query = """
        SELECT 
            dd.year,
            dd.month,
            dd.month_name,
            dp.category,
            du.city,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            COUNT(fs.order_number) AS total_orders
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        JOIN dim_product dp ON fs.product_key = dp.product_key
        JOIN dim_user du ON fs.customer_key = du.user_key
        WHERE dd.year = %s AND dd.month = %s
        GROUP BY dd.year, dd.month, dd.month_name, dp.category, du.city
        ORDER BY total_sales DESC;
    """
    params = (year, month)
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=params)
        duration = time.perf_counter() - start_time
        return df, duration, query, params
    except Exception as e:
        st.error(f"Failed to execute month slice query: {e}")
        return pd.DataFrame(), 0.0, query, params