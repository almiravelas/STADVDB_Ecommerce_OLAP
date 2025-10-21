import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
from typing import Optional, List

@st.cache_data(ttl=600)
def get_product_data(_engine: Engine, years: Optional[List[int]] = None) -> pd.DataFrame:
    """
    Queries the data warehouse to get sales data joined with product dimension details.
    The results are cached for performance.

    This version is optimized by:
    1.  Assuming that indexes exist on the foreign key columns (product_key, date_key)
        in the fact_sales table.
        - SQL to create indexes:
          CREATE INDEX idx_fs_product_key ON fact_sales(product_key);
          CREATE INDEX idx_fs_date_key ON fact_sales(date_key);
    2.  Allowing optional filtering by year to reduce the amount of data pulled.
    """
    # Return an empty DataFrame if no database connection is provided
    if _engine is None:
        return pd.DataFrame(), 0.0  # <-- Return tuple

    # Base SQL query
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
        JOIN dim_date dd ON fs.date_key = dd.date_key
    """

    params = {}
    # Add a WHERE clause if years are provided for filtering
    if years:
        query += " WHERE dd.year IN %(years)s"
        params['years'] = tuple(years)

    query += ";" # End the query

    try:
        # --- MODIFICATION: Start timer ---
        start_time = time.perf_counter() # <-- Add timer start
        
        # Execute the query and load the result into a pandas DataFrame
        # Using 'params' helps prevent SQL injection
        df = pd.read_sql(query, _engine, params=params)
        return df
    except Exception as e:
        # Display an error in the Streamlit app if the query fails
        st.error(f"Failed to load product data: {e}")
        return pd.DataFrame()

# Example of how you might call this in your Streamlit app
# db_engine = create_your_db_engine()
# data_all_years = get_product_data(db_engine)
# data_2024_2025 = get_product_data(db_engine, years=[2024, 2025])
