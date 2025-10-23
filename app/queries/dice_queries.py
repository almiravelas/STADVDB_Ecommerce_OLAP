"""
Dice Operation - Multiple values per dimension
Optimized for performance with pagination and improved AOV logic.
"""
import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
import time

# --- OPTIMIZATION 1: Improved AOV Logic ---
# Using COUNT(DISTINCT fs.order_number) is more accurate for AOV
# if the fact_sales table is at the order-line grain.
AOV_EXPR = "SUM(fs.sales_amount)/NULLIF(COUNT(DISTINCT fs.order_number),0)"


@st.cache_data(ttl=300)  # Cache for 5 minutes
def dice_multi_dimension(
    _engine: Engine, 
    years: list = None, 
    categories: list = None, 
    cities: list = None, 
    couriers: list = None,
    page: int = 1,        # --- OPTIMIZATION 2: Add pagination argument
    page_size: int = 1000 # --- OPTIMIZATION 2: Add page size argument
) -> tuple[pd.DataFrame, float, int]:
    """
    Dice data across multiple dimensions including rider/courier.
    
    Optimized to use pagination (LIMIT/OFFSET) for faster app performance.
    Returns (DataFrame, query_duration, total_row_count)
    """
    if _engine is None:
        return pd.DataFrame(), 0.0, 0
    
    years = years or []
    categories = categories or []
    cities = cities or []
    couriers = couriers or []
    
    if page < 1:
        page = 1
    
    # Calculate offset for pagination
    offset = (page - 1) * page_size

    # Build safe WHERE clause with parameter placeholders
    clauses = []
    params_dict = {}
    if years:
        clauses.append("dd.year IN (%(years)s)")
        params_dict['years'] = tuple(years)
    if categories:
        clauses.append("dp.category IN (%(categories)s)")
        params_dict['categories'] = tuple(categories)
    if cities:
        clauses.append("du.city IN (%(cities)s)")
        params_dict['cities'] = tuple(cities)
    if couriers:
        clauses.append("dr.courier_name IN (%(couriers)s)")
        params_dict['couriers'] = tuple(couriers)

    where_sql = " AND ".join(clauses) if clauses else "1=1"
    
    # --- OPTIMIZATION 3: Use a Common Table Expression (CTE) ---
    # This makes the query cleaner and allows us to get the COUNT(*)
    # and the paginated data in a single logical query.
    
    cte_sql = f"""
        WITH FilteredGroupedData AS (
            SELECT 
                dd.year,
                dd.month_name,
                dp.category,
                dp.product_name,
                du.city,
                dr.courier_name,
                dr.vehicleType,
                COUNT(fs.order_number) AS total_orders,
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
        )
    """
    
    # Query 1: Get the paginated data
    # --- OPTIMIZATION 4: Remove ORDER BY from SQL ---
    # We will sort in pandas after fetching the smaller, paginated data.
    # This is often faster as it reduces load on the DB.
    data_query = f"""
        {cte_sql}
        SELECT * FROM FilteredGroupedData
        -- We apply a default order just to make LIMIT/OFFSET stable
        ORDER BY year, month_name, category, product_name 
        LIMIT %(page_size)s OFFSET %(offset)s;
    """
    
    # Query 2: Get the *total* count of rows (for pagination controls)
    count_query = f"""
        {cte_sql}
        SELECT COUNT(*) AS total_rows FROM FilteredGroupedData;
    """
    
    # Add pagination params to the dictionary
    params_dict['page_size'] = page_size
    params_dict['offset'] = offset
    
    try:
        start_time = time.perf_counter()
        
        # --- NOTE on parameter substitution ---
        # pd.read_sql handles different paramstyles (%s vs %(name)s).
        # We must convert our dictionary to a tuple for the %s style used
        # in the original code, IF we stick to that.
        # However, `%(name)s` (dict) style is generally cleaner.
        # Let's adapt to the dict-style (%(name)s) which pandas/sqlalchemy supports.
        #
        # Re-building params for `pd.read_sql` which prefers positional %s
        # or a dict for named parameters (which varies by DB driver).
        # Let's stick to the original's `%s` style for compatibility.

        params_list: list = []
        sql_placeholders = []
        
        if years:
            placeholders = ",".join(["%s"] * len(years))
            sql_placeholders.append(f"dd.year IN ({placeholders})")
            params_list.extend(years)
        if categories:
            placeholders = ",".join(["%s"] * len(categories))
            sql_placeholders.append(f"dp.category IN ({placeholders})")
            params_list.extend(categories)
        if cities:
            placeholders = ",".join(["%s"] * len(cities))
            sql_placeholders.append(f"du.city IN ({placeholders})")
            params_list.extend(cities)
        if couriers:
            placeholders = ",".join(["%s"] * len(couriers))
            sql_placeholders.append(f"dr.courier_name IN ({placeholders})")
            params_list.extend(couriers)
        
        safe_where_sql = " AND ".join(sql_placeholders) if sql_placeholders else "1=1"

        # Rebuild the final queries with %s placeholders
        cte_sql_final = f"""
            WITH FilteredGroupedData AS (
                SELECT 
                    dd.year, dd.month_name, dp.category, dp.product_name,
                    du.city, dr.courier_name, dr.vehicleType,
                    COUNT(fs.order_number) AS total_orders,
                    SUM(fs.sales_amount) AS total_sales,
                    SUM(fs.quantity) AS total_quantity,
                    {AOV_EXPR} AS avg_order_value
                FROM fact_sales fs
                JOIN dim_date dd   ON fs.date_key   = dd.date_key
                JOIN dim_product dp ON fs.product_key = dp.product_key
                JOIN dim_user du    ON fs.customer_key = du.user_key
                JOIN dim_rider dr   ON fs.rider_key    = dr.rider_key
                WHERE {safe_where_sql}
                GROUP BY dd.year, dd.month_name, dp.category, dp.product_name, du.city, dr.courier_name, dr.vehicleType
            )
        """
        
        data_query_final = f"""
            {cte_sql_final}
            SELECT * FROM FilteredGroupedData
            ORDER BY total_sales DESC -- Re-instating ORDER BY as it's needed for TOP N
            LIMIT %s OFFSET %s;
        """
        
        count_query_final = f"""
            {cte_sql_final}
            SELECT COUNT(*) AS total_rows FROM FilteredGroupedData;
        """

        # Execute data query
        data_params = tuple(params_list) + (page_size, offset)
        df = pd.read_sql(data_query_final, _engine, params=data_params)
        
        # Execute count query
        count_params = tuple(params_list)
        total_rows_df = pd.read_sql(count_query_final, _engine, params=count_params)
        total_rows = total_rows_df['total_rows'].iloc[0] if not total_rows_df.empty else 0

        duration = time.perf_counter() - start_time
        
        # --- OPTIMIZATION 5: Sort in Pandas ---
        # If you remove ORDER BY from SQL, you can sort here.
        # Since we added it back to get the *Top N* results, this step
        # isn't strictly necessary, but is good practice if you
        # were fetching an arbitrary page.
        # df = df.sort_values('total_sales', ascending=False)

        return df, duration, int(total_rows)
        
    except Exception as e:
        st.error(f"Failed to execute optimized dice query: {e}")
        return pd.DataFrame(), 0.0, 0