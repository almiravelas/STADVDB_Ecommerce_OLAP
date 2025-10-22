"""
Drill-down Operations - Disaggregation to lower granularity
"""
import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
import time

AOV_EXPR = "SUM(fs.sales_amount)/NULLIF(COUNT(DISTINCT fs.order_number),0)"


@st.cache_data(ttl=600)
def drilldown_year_to_month(_engine: Engine, year: int) -> tuple[pd.DataFrame, float]:
    """Drill down from year to month level"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
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
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=(year,))
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute drill-down query: {e}")
        return pd.DataFrame(), 0.0


@st.cache_data(ttl=600)
def drilldown_month_to_day(_engine: Engine, year: int, month: int) -> tuple[pd.DataFrame, float]:
    """Drill down from month to day level"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
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
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=(year, month))
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute drill-down query: {e}")
        return pd.DataFrame(), 0.0


@st.cache_data(ttl=600)
def drilldown_category_to_product(_engine: Engine, category: str) -> tuple[pd.DataFrame, float]:
    """Drill down from category to individual products"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
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
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=(category,))
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute drill-down query: {e}")
        return pd.DataFrame(), 0.0


@st.cache_data(ttl=600)
def drilldown_courier_to_vehicle(_engine: Engine, courier: str) -> tuple[pd.DataFrame, float]:
    """Drill down from courier to vehicle type and other attributes"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    query = f"""
        SELECT 
            dr.courier_name,
            dr.vehicleType,
            dd.year,
            dd.month_name,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            {AOV_EXPR} AS avg_order_value
        FROM fact_sales fs
        JOIN dim_rider dr ON fs.rider_key = dr.rider_key
        JOIN dim_date dd ON fs.date_key = dd.date_key
        WHERE dr.courier_name = %s
        GROUP BY dr.courier_name, dr.vehicleType, dd.year, dd.month_name
        ORDER BY dd.year, dd.month_name, total_sales DESC;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=(courier,))
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute courier drill-down query: {e}")
        return pd.DataFrame(), 0.0
