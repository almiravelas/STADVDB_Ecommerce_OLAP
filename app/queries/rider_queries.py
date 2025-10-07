import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine

@st.cache_data
def get_sales_with_rider_details(_engine: Engine) -> pd.DataFrame:
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
        st.error(f"Failed to load rider data: {e}")
        return pd.DataFrame()
