"""
Dice Operation - Multiple values per dimension
"""
import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
import time

AOV_EXPR = "SUM(fs.sales_amount)/NULLIF(COUNT(DISTINCT fs.order_number),0)"


@st.cache_data(ttl=600)
def dice_multi_dimension(
    _engine: Engine, 
    years: list = None, 
    categories: list = None, 
    cities: list = None, 
    couriers: list = None
) -> tuple[pd.DataFrame, float]:
    """Dice data across multiple dimensions including rider/courier"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    years = years or []
    categories = categories or []
    cities = cities or []
    couriers = couriers or []

    # Build safe WHERE clause with parameter placeholders
    clauses = []
    params: list = []
    if years:
        placeholders = ",".join(["%s"] * len(years))
        clauses.append(f"dd.year IN ({placeholders})")
        params.extend(years)
    if categories:
        placeholders = ",".join(["%s"] * len(categories))
        clauses.append(f"dp.category IN ({placeholders})")
        params.extend(categories)
    if cities:
        placeholders = ",".join(["%s"] * len(cities))
        clauses.append(f"du.city IN ({placeholders})")
        params.extend(cities)
    if couriers:
        placeholders = ",".join(["%s"] * len(couriers))
        clauses.append(f"dr.courier_name IN ({placeholders})")
        params.extend(couriers)

    where_sql = " AND ".join(clauses) if clauses else "1=1"
    
    query = f"""
        SELECT 
            dd.year,
            dd.month_name,
            dp.category,
            dp.product_name,
            du.city,
            dr.courier_name,
            dr.vehicleType,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            {AOV_EXPR} AS avg_order_value
        FROM fact_sales fs
        JOIN dim_date dd   ON fs.date_key   = dd.date_key
        JOIN dim_product dp ON fs.product_key = dp.product_key
        JOIN dim_user du    ON fs.customer_key = du.user_key
        JOIN dim_rider dr   ON fs.rider_key    = dr.rider_key
        WHERE {where_sql}
        GROUP BY dd.year, dd.month_name, dp.category, dp.product_name, du.city, dr.courier_name, dr.vehicleType
        ORDER BY total_sales DESC;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=tuple(params))
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute dice query: {e}")
        return pd.DataFrame(), 0.0
