import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine

@st.cache_data(ttl=600)
def get_product_data(_engine: Engine) -> pd.DataFrame:
    """
    Queries the data warehouse to get sales data joined with product dimension details.
    The results are cached for performance.
    """
    #
    # Return an empty DataFrame if no database connection is provided
    if _engine is None:
        return pd.DataFrame()

    # SQL query to join the sales fact table with the product dimension table
    query = """
        SELECT
            fs.sales_amount AS total_sales,
            fs.quantity,
            dp.product_name,
            dp.category,
            dp.price,
            dd.year,
            dd.month_name
        FROM fact_sales fs
        JOIN dim_product dp ON fs.product_key = dp.product_key
        JOIN dim_date dd ON fs.date_key = dd.date_key;
    """
    try:
        # Execute the query and load the result into a pandas DataFrame
        df = pd.read_sql(query, _engine)
        return df
    except Exception as e:
        # Display an error in the Streamlit app if the query fails
        st.error(f"Failed to load product data: {e}")
        return pd.DataFrame()