"""
Drill-down Operations - Disaggregation to lower granularity
"""
import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
import time

AOV_EXPR = "SUM(fs.sales_amount)/NULLIF(COUNT(DISTINCT fs.order_number),0)"


@st.cache_data(ttl=300)  # Cache for 5 minutes
def drilldown_year_to_month(_engine: Engine, year: int) -> tuple[pd.DataFrame, float, str, tuple | None]:
    """Drill down from year to month level"""
    if _engine is None:
        return pd.DataFrame(), 0.0, "", None
    
    query = f"""
        SELECT 
            dd.year,
            dd.month,
            dd.month_name,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            {AOV_EXPR} AS avg_order_value
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        WHERE dd.year = %s
        GROUP BY dd.year, dd.month, dd.month_name
        ORDER BY dd.month;
    """
    params = (year,)
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=params)
        duration = time.perf_counter() - start_time
        return df, duration, query, params
    except Exception as e:
        st.error(f"Failed to execute drill-down query: {e}")
        return pd.DataFrame(), 0.0, query, params


# @st.cache_data(ttl=300)  # Cache for 5 minutes
def drilldown_month_to_day(_engine: Engine, year: int, month: int) -> tuple[pd.DataFrame, float, str, tuple | None]:
    """Drill down from month to day level"""
    if _engine is None:
        return pd.DataFrame(), 0.0, "", None
    
    query = f"""
        SELECT 
            dd.full_date,
            dd.day_name,
            dd.is_weekend,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            {AOV_EXPR} AS avg_order_value
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        WHERE dd.year = %s AND dd.month = %s
        GROUP BY dd.full_date, dd.day_name, dd.is_weekend
        ORDER BY dd.full_date;
    """
    params = (year, month)
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=params)
        duration = time.perf_counter() - start_time
        return df, duration, query, params
    except Exception as e:
        st.error(f"Failed to execute drill-down query: {e}")
        return pd.DataFrame(), 0.0, query, params


# @st.cache_data(ttl=300)  # Cache for 5 minutes
def drilldown_category_to_product(_engine: Engine, category: str) -> tuple[pd.DataFrame, float, str, tuple | None]:
    """Drill down from category to individual products"""
    if _engine is None:
        return pd.DataFrame(), 0.0, "", None
    
    query = f"""
        SELECT 
            dp.category,
            dp.product_name,
            dp.price,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            {AOV_EXPR} AS avg_order_value
        FROM fact_sales fs
        JOIN dim_product dp ON fs.product_key = dp.product_key
        WHERE dp.category = %s
        GROUP BY dp.category, dp.product_name, dp.price
        ORDER BY total_sales DESC;
    """
    params = (category,)
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=params)
        duration = time.perf_counter() - start_time
        return df, duration, query, params
    except Exception as e:
        st.error(f"Failed to execute drill-down query: {e}")
        return pd.DataFrame(), 0.0, query, params


# @st.cache_data(ttl=300)  # Cache for 5 minutes
def drilldown_courier_to_vehicle(_engine: Engine, courier: str) -> tuple[pd.DataFrame, float, str, tuple | None]:
    """Drill down from courier to vehicle type and other attributes"""
    if _engine is None:
        return pd.DataFrame(), 0.0, "", None
    
    query = f"""
        SELECT 
            dr.courier_name,
            dr.vehicleType,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            {AOV_EXPR} AS avg_order_value,
            COUNT(DISTINCT fs.rider_key) AS rider_count
        FROM fact_sales fs
        JOIN dim_rider dr ON fs.rider_key = dr.rider_key
        WHERE dr.courier_name = %s
        GROUP BY dr.courier_name, dr.vehicleType
        ORDER BY total_sales DESC;
    """
    # Note: Simplified GROUP BY based on your drilldown_view.py (it doesn't use time)
    # If you need time, add dd.year, dd.month_name back and JOIN dim_date
    params = (courier,)
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=params)
        duration = time.perf_counter() - start_time
        return df, duration, query, params
    except Exception as e:
        st.error(f"Failed to execute courier drill-down query: {e}")
        return pd.DataFrame(), 0.0, query, params


# @st.cache_data(ttl=300)  # Cache for 5 minutes
def drilldown_region_to_country(_engine: Engine, continent: str) -> tuple[pd.DataFrame, float, str, tuple | None]:
    """Drill down from region/continent to country level"""
    if _engine is None:
        return pd.DataFrame(), 0.0, "", None
    
    query = f"""
        SELECT 
            du.continent,
            du.country,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            {AOV_EXPR} AS avg_order_value,
            COUNT(DISTINCT du.city) AS city_count
        FROM fact_sales fs
        JOIN dim_user du ON fs.customer_key = du.user_key
        WHERE du.continent = %s
        GROUP BY du.continent, du.country
        ORDER BY total_sales DESC;
    """
    params = (continent,)
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=params)
        duration = time.perf_counter() - start_time
        return df, duration, query, params
    except Exception as e:
        st.error(f"Failed to execute region drill-down query: {e}")
        return pd.DataFrame(), 0.0, query, params