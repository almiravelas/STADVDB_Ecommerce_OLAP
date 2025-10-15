import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine


@st.cache_data
def get_sales_per_month(_engine: Engine) -> pd.DataFrame:
    """Returns total sales per month per year."""
    if _engine is None:
        return pd.DataFrame()

    query = """
        SELECT 
            dd.year,
            dd.month,
            dd.month_name,
            SUM(fs.sales_amount) AS total_sales
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        GROUP BY dd.year, dd.month, dd.month_name
        ORDER BY dd.year, dd.month;
    """
    try:
        return pd.read_sql(query, _engine)
    except Exception as e:
        st.error(f"Failed to load sales per month: {e}")
        return pd.DataFrame()


@st.cache_data
def get_sales_per_year(_engine: Engine) -> pd.DataFrame:
    """Returns total sales per year."""
    if _engine is None:
        return pd.DataFrame()

    query = """
        SELECT 
            dd.year,
            SUM(fs.sales_amount) AS total_sales
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        GROUP BY dd.year
        ORDER BY dd.year;
    """
    try:
        return pd.read_sql(query, _engine)
    except Exception as e:
        st.error(f"Failed to load sales per year: {e}")
        return pd.DataFrame()


@st.cache_data
def get_sales_by_day_of_week(_engine: Engine) -> pd.DataFrame:
    """Returns total sales grouped by day of the week."""
    if _engine is None:
        return pd.DataFrame()

    query = """
        SELECT 
            dd.day_name,
            SUM(fs.sales_amount) AS total_sales
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        GROUP BY dd.day_name
        ORDER BY 
            FIELD(dd.day_name, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday');
    """
    try:
        return pd.read_sql(query, _engine)
    except Exception as e:
        st.error(f"Failed to load sales by day of week: {e}")
        return pd.DataFrame()


@st.cache_data
def get_sales_weekend_vs_weekday(_engine: Engine) -> pd.DataFrame:
    """Returns total sales comparing weekend vs weekday."""
    if _engine is None:
        return pd.DataFrame()

    query = """
        SELECT 
            dd.is_weekend,
            SUM(fs.sales_amount) AS total_sales
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        GROUP BY dd.is_weekend;
    """
    try:
        return pd.read_sql(query, _engine)
    except Exception as e:
        st.error(f"Failed to load weekend vs weekday sales: {e}")
        return pd.DataFrame()


@st.cache_data
def get_daily_sales_trend(_engine: Engine) -> pd.DataFrame:
    """Returns daily sales trends for time-series visualization."""
    if _engine is None:
        return pd.DataFrame()

    query = """
        SELECT 
            dd.full_date,
            SUM(fs.sales_amount) AS total_sales
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        GROUP BY dd.full_date
        ORDER BY dd.full_date;
    """
    try:
        return pd.read_sql(query, _engine)
    except Exception as e:
        st.error(f"Failed to load daily sales trend: {e}")
        return pd.DataFrame()
