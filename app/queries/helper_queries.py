"""
Helper Queries - Lookup and filter options for OLAP operations
"""
import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine


@st.cache_data(ttl=600)
def get_available_years(_engine: Engine) -> list:
    """Get list of available years (from dim_date)"""
    if _engine is None:
        return []
    query = "SELECT DISTINCT year FROM dim_date ORDER BY year"
    try:
        df = pd.read_sql(query, _engine)
        return df['year'].tolist()
    except Exception as e:
        st.error(f"Failed to get years: {e}")
        return []


@st.cache_data(ttl=600)
def get_available_categories(_engine: Engine) -> list:
    """Get list of available product categories"""
    if _engine is None:
        return []
    query = "SELECT DISTINCT category FROM dim_product ORDER BY category"
    try:
        df = pd.read_sql(query, _engine)
        return df['category'].tolist()
    except Exception as e:
        st.error(f"Failed to get categories: {e}")
        return []


@st.cache_data(ttl=600)
def get_available_cities(_engine: Engine) -> list:
    """Get list of available user cities"""
    if _engine is None:
        return []
    query = "SELECT DISTINCT city FROM dim_user ORDER BY city"
    try:
        df = pd.read_sql(query, _engine)
        return df['city'].tolist()
    except Exception as e:
        st.error(f"Failed to get cities: {e}")
        return []


@st.cache_data(ttl=600)
def get_available_couriers(_engine: Engine) -> list:
    """Get list of available courier names"""
    if _engine is None:
        return []
    query = "SELECT DISTINCT courier_name FROM dim_rider ORDER BY courier_name"
    try:
        df = pd.read_sql(query, _engine)
        return df['courier_name'].tolist()
    except Exception as e:
        st.error(f"Failed to get couriers: {e}")
        return []


@st.cache_data(ttl=600)
def get_available_vehicle_types(_engine: Engine) -> list:
    """Get list of available rider vehicle types"""
    if _engine is None:
        return []
    query = "SELECT DISTINCT vehicleType FROM dim_rider ORDER BY vehicleType"
    try:
        df = pd.read_sql(query, _engine)
        return df['vehicleType'].tolist()
    except Exception as e:
        st.error(f"Failed to get vehicle types: {e}")
        return []
