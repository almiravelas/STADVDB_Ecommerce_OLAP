import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine

# --- Query 1: Fetching Detailed Data for In-App OLAP ---
# OLAP Type: Enables in-app SLICE, DICE, and DRILL-DOWN / ROLL-UP.
# This is the primary query for the interactive dashboard. It fetches the most granular
# data, allowing for maximum flexibility in the application layer using Pandas.
@st.cache_data
def get_sales_with_rider_details(_engine: Engine) -> pd.DataFrame:
    """
    Fetches raw sales data joined with rider details without pre-aggregation.
    This allows for flexible filtering and grouping in the Streamlit app.
    """
    if _engine is None:
        return pd.DataFrame()

    query = """
        SELECT
            fs.order_number,
            fs.quantity,
            fs.unit_price,
            fs.sales_amount,
            dr.rider_name,
            dr.vehicleType,
            dr.gender,
            dr.age,
            dr.courier_name
        FROM fact_sales fs
        JOIN dim_rider dr ON fs.rider_key = dr.rider_key;
    """
    
    try:
        df = pd.read_sql(query, _engine)
        return df
    except Exception as e:
        st.error(f"Failed to execute query. Error: {e}")
        return pd.DataFrame()

# --- Query 2: Pre-computed Hierarchical Aggregation ---
# OLAP Type: ROLL-UP
# This query uses the database's processing power to generate a summary report with
# hierarchical subtotals and a grand total. It's ideal for reports where you need to see
# data aggregated at multiple levels simultaneously (e.g., sales per vehicle type,
# then per courier, and then the overall total).
@st.cache_data
def get_sales_rollup_by_courier_vehicle(_engine: Engine) -> pd.DataFrame:
    """
    Generates a hierarchical sales summary using ROLLUP.
    """
    if _engine is None:
        return pd.DataFrame()

    query = """
        SELECT
            COALESCE(dr.courier_name, 'All Couriers') AS courier_name,
            COALESCE(dr.vehicleType, 'All Vehicle Types') AS vehicle_type,
            SUM(fs.sales_amount) AS total_sales
        FROM fact_sales fs
        JOIN dim_rider dr ON fs.rider_key = dr.rider_key
        GROUP BY ROLLUP(dr.courier_name, dr.vehicleType);
    """
    
    try:
        df = pd.read_sql(query, _engine)
        return df
    except Exception as e:
        st.error(f"Failed to execute rollup query. Error: {e}")
        return pd.DataFrame()

# --- Query 3: Pivoted Comparative Analysis ---
# OLAP Type: PIVOT
# This query transforms data from rows into columns, which is useful for creating
# crosstab-style reports for easy comparison. Here, we pivot the rider gender to
# directly compare sales performance between male and female riders for each courier.
@st.cache_data
def get_sales_pivoted_by_gender(_engine: Engine) -> pd.DataFrame:
    """
    Pivots sales data to compare male vs. female rider performance per courier.
    """
    if _engine is None:
        return pd.DataFrame()
        
    query = """
        SELECT
            dr.courier_name,
            SUM(CASE WHEN dr.gender = 'Male' THEN fs.sales_amount ELSE 0 END) AS male_sales,
            SUM(CASE WHEN dr.gender = 'Female' THEN fs.sales_amount ELSE 0 END) AS female_sales,
            SUM(fs.sales_amount) AS total_sales
        FROM fact_sales fs
        JOIN dim_rider dr ON fs.rider_key = dr.rider_key
        GROUP BY dr.courier_name;
    """

    try:
        df = pd.read_sql(query, _engine)
        return df
    except Exception as e:
        st.error(f"Failed to execute pivot query. Error: {e}")
        return pd.DataFrame()