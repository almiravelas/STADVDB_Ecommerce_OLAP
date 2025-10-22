"""
OLAP Operations Queries
Contains queries for Roll-up, Drill-down, Slice, Dice, and Pivot operations
"""
import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
import time


# ============================================================================
# ROLL-UP OPERATIONS (Aggregation to higher level of granularity)
# ============================================================================

@st.cache_data(ttl=600)
def rollup_sales_by_year(_engine: Engine) -> tuple[pd.DataFrame, float]:
    """Roll up sales data to year level (highest granularity)"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    query = """
        SELECT 
            dd.year,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            AVG(fs.sales_amount) AS avg_order_value
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        GROUP BY dd.year
        ORDER BY dd.year;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute roll-up query: {e}")
        return pd.DataFrame(), 0.0


@st.cache_data(ttl=600)
def rollup_sales_by_quarter(_engine: Engine) -> tuple[pd.DataFrame, float]:
    """Roll up sales data to quarter level"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    query = """
        SELECT 
            dd.year,
            dd.quarter,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            AVG(fs.sales_amount) AS avg_order_value
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        GROUP BY dd.year, dd.quarter
        ORDER BY dd.year, dd.quarter;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute roll-up query: {e}")
        return pd.DataFrame(), 0.0


@st.cache_data(ttl=600)
def rollup_sales_by_category(_engine: Engine) -> tuple[pd.DataFrame, float]:
    """Roll up sales data by product category"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    query = """
        SELECT 
            dp.category,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            AVG(fs.sales_amount) AS avg_order_value,
            COUNT(DISTINCT dp.product_key) AS product_count
        FROM fact_sales fs
        JOIN dim_product dp ON fs.product_key = dp.product_key
        GROUP BY dp.category
        ORDER BY total_sales DESC;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute roll-up query: {e}")
        return pd.DataFrame(), 0.0


# ============================================================================
# DRILL-DOWN OPERATIONS (Disaggregation to lower level of granularity)
# ============================================================================

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
            AVG(fs.sales_amount) AS avg_order_value
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        WHERE dd.year = {year}
        GROUP BY dd.year, dd.month, dd.month_name
        ORDER BY dd.month;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
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
    
    query = """
        SELECT 
            dp.category,
            dp.product_name,
            dp.price,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            AVG(fs.sales_amount) AS avg_order_value
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
            AVG(fs.sales_amount) AS avg_order_value
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        WHERE dd.year = {year} AND dd.month = {month}
        GROUP BY dd.full_date, dd.day_name, dd.is_weekend
        ORDER BY dd.full_date;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute drill-down query: {e}")
        return pd.DataFrame(), 0.0


# ============================================================================
# SLICE OPERATIONS (Selecting a single dimension value)
# ============================================================================

@st.cache_data(ttl=600)
def slice_by_year(_engine: Engine, year: int) -> tuple[pd.DataFrame, float]:
    """Slice data for a specific year across all dimensions"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    query = f"""
        SELECT 
            dd.month_name,
            dp.category,
            du.city AS user_city,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            COUNT(DISTINCT fs.order_number) AS total_orders
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        JOIN dim_product dp ON fs.product_key = dp.product_key
        JOIN dim_user du ON fs.customer_key = du.user_key
        WHERE dd.year = {year}
        GROUP BY dd.month_name, dp.category, du.city
        ORDER BY total_sales DESC
        LIMIT 1000;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute slice query: {e}")
        return pd.DataFrame(), 0.0


@st.cache_data(ttl=600)
def slice_by_category(_engine: Engine, category: str) -> tuple[pd.DataFrame, float]:
    """Slice data for a specific product category"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    query = """
        SELECT 
            dd.year,
            dd.month_name,
            dp.product_name,
            du.city AS user_city,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            COUNT(DISTINCT fs.order_number) AS total_orders
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        JOIN dim_product dp ON fs.product_key = dp.product_key
        JOIN dim_user du ON fs.customer_key = du.user_key
        WHERE dp.category = %s
        GROUP BY dd.year, dd.month_name, dp.product_name, du.city
        ORDER BY total_sales DESC
        LIMIT 1000;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=(category,))
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute slice query: {e}")
        return pd.DataFrame(), 0.0


@st.cache_data(ttl=600)
def slice_by_city(_engine: Engine, city: str) -> tuple[pd.DataFrame, float]:
    """Slice data for a specific user city"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    query = """
        SELECT 
            dd.year,
            dd.month_name,
            dp.category,
            dp.product_name,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            COUNT(DISTINCT fs.order_number) AS total_orders
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        JOIN dim_product dp ON fs.product_key = dp.product_key
        JOIN dim_user du ON fs.customer_key = du.user_key
        WHERE du.city = %s
        GROUP BY dd.year, dd.month_name, dp.category, dp.product_name
        ORDER BY total_sales DESC
        LIMIT 1000;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params=(city,))
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute slice query: {e}")
        return pd.DataFrame(), 0.0


# ============================================================================
# DICE OPERATIONS (Selecting multiple dimension values)
# ============================================================================

@st.cache_data(ttl=600)
def dice_multi_dimension(_engine: Engine, years: list, categories: list, cities: list, couriers: list = None) -> tuple[pd.DataFrame, float]:
    """Dice data across multiple dimensions including rider/courier"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    # Build WHERE clause dynamically
    where_clauses = []
    if years:
        year_list = ','.join(map(str, years))
        where_clauses.append(f"dd.year IN ({year_list})")
    if categories:
        cat_list = ','.join([f"'{c}'" for c in categories])
        where_clauses.append(f"dp.category IN ({cat_list})")
    if cities:
        city_list = ','.join([f"'{c}'" for c in cities])
        where_clauses.append(f"du.city IN ({city_list})")
    if couriers:
        courier_list = ','.join([f"'{c}'" for c in couriers])
        where_clauses.append(f"dr.courier_name IN ({courier_list})")
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    query = f"""
        SELECT 
            dd.year,
            dd.month_name,
            dp.category,
            dp.product_name,
            du.city AS user_city,
            dr.courier_name,
            dr.vehicleType,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            COUNT(DISTINCT fs.order_number) AS total_orders
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        JOIN dim_product dp ON fs.product_key = dp.product_key
        JOIN dim_user du ON fs.customer_key = du.user_key
        JOIN dim_rider dr ON fs.rider_key = dr.rider_key
        WHERE {where_sql}
        GROUP BY dd.year, dd.month_name, dp.category, dp.product_name, du.city, dr.courier_name, dr.vehicleType
        ORDER BY total_sales DESC
        LIMIT 1000;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute dice query: {e}")
        return pd.DataFrame(), 0.0


# ============================================================================
# PIVOT OPERATIONS (Rotating data for different perspectives)
# ============================================================================

@st.cache_data(ttl=600)
def pivot_category_by_month(_engine: Engine) -> tuple[pd.DataFrame, float]:
    """Pivot: Categories as rows, months as columns"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    query = """
        SELECT 
            dp.category,
            dd.year,
            dd.month,
            dd.month_name,
            SUM(fs.sales_amount) AS total_sales
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        JOIN dim_product dp ON fs.product_key = dp.product_key
        GROUP BY dp.category, dd.year, dd.month, dd.month_name
        ORDER BY dp.category, dd.year, dd.month;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute pivot query: {e}")
        return pd.DataFrame(), 0.0


@st.cache_data(ttl=600)
def pivot_city_by_category(_engine: Engine) -> tuple[pd.DataFrame, float]:
    """Pivot: Cities as rows, categories as columns"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    query = """
        SELECT 
            du.city,
            dp.category,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity
        FROM fact_sales fs
        JOIN dim_product dp ON fs.product_key = dp.product_key
        JOIN dim_user du ON fs.customer_key = du.user_key
        GROUP BY du.city, dp.category
        ORDER BY du.city, dp.category;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute pivot query: {e}")
        return pd.DataFrame(), 0.0


@st.cache_data(ttl=600)
def pivot_year_by_quarter(_engine: Engine) -> tuple[pd.DataFrame, float]:
    """Pivot: Years as rows, quarters as columns"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    query = """
        SELECT 
            dd.year,
            dd.quarter,
            SUM(fs.sales_amount) AS total_sales,
            COUNT(DISTINCT fs.order_number) AS total_orders
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        GROUP BY dd.year, dd.quarter
        ORDER BY dd.year, dd.quarter;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute pivot query: {e}")
        return pd.DataFrame(), 0.0


# ============================================================================
# HELPER QUERIES (Get distinct values for filters)
# ============================================================================

@st.cache_data(ttl=600)
def get_available_years(_engine: Engine) -> list:
    """Get list of available years (filtered to 2024 and 2025 only)"""
    if _engine is None:
        return []
    
    query = "SELECT DISTINCT year FROM dim_date WHERE year IN (2024, 2025) ORDER BY year"
    try:
        df = pd.read_sql(query, _engine)
        return df['year'].tolist()
    except Exception as e:
        st.error(f"Failed to get years: {e}")
        return []
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
    """Get list of available courier companies"""
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
    """Get list of available vehicle types"""
    if _engine is None:
        return []
    
    query = "SELECT DISTINCT vehicleType FROM dim_rider ORDER BY vehicleType"
    try:
        df = pd.read_sql(query, _engine)
        return df['vehicleType'].tolist()
    except Exception as e:
        st.error(f"Failed to get vehicle types: {e}")
        return []


# ============================================================================
# RIDER DIMENSION OLAP OPERATIONS
# ============================================================================

@st.cache_data(ttl=600)
def rollup_sales_by_courier(_engine: Engine) -> tuple[pd.DataFrame, float]:
    """Roll up sales data to courier level"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    query = """
        SELECT 
            dr.courier_name,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            AVG(fs.sales_amount) AS avg_order_value,
            COUNT(DISTINCT dr.rider_key) AS rider_count
        FROM fact_sales fs
        JOIN dim_rider dr ON fs.rider_key = dr.rider_key
        GROUP BY dr.courier_name
        ORDER BY total_sales DESC;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine)
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute courier roll-up query: {e}")
        return pd.DataFrame(), 0.0


@st.cache_data(ttl=600)
def drilldown_courier_to_vehicle(_engine: Engine, courier: str) -> tuple[pd.DataFrame, float]:
    """Drill down from courier to vehicle type level"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    query = """
        SELECT 
            dr.vehicleType,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            AVG(fs.sales_amount) AS avg_order_value,
            COUNT(DISTINCT dr.rider_key) AS rider_count
        FROM fact_sales fs
        JOIN dim_rider dr ON fs.rider_key = dr.rider_key
        WHERE dr.courier_name = :courier
        GROUP BY dr.vehicleType
        ORDER BY total_sales DESC;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params={'courier': courier})
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute courier drill-down query: {e}")
        return pd.DataFrame(), 0.0


@st.cache_data(ttl=600)
def slice_by_courier(_engine: Engine, courier: str) -> tuple[pd.DataFrame, float]:
    """Slice data by a specific courier"""
    if _engine is None:
        return pd.DataFrame(), 0.0
    
    query = """
        SELECT 
            dr.courier_name,
            dd.year,
            dd.month_name,
            dp.category,
            du.city,
            dr.vehicleType,
            COUNT(DISTINCT fs.order_number) AS total_orders,
            SUM(fs.sales_amount) AS total_sales,
            SUM(fs.quantity) AS total_quantity,
            AVG(fs.sales_amount) AS avg_order_value
        FROM fact_sales fs
        JOIN dim_rider dr ON fs.rider_key = dr.rider_key
        JOIN dim_date dd ON fs.date_key = dd.date_key
        JOIN dim_product dp ON fs.product_key = dp.product_key
        JOIN dim_user du ON fs.customer_key = du.user_key
        WHERE dr.courier_name = :courier
        GROUP BY dr.courier_name, dd.year, dd.month_name, dp.category, du.city, dr.vehicleType
        ORDER BY dd.year, dd.month_name, total_sales DESC;
    """
    try:
        start_time = time.perf_counter()
        df = pd.read_sql(query, _engine, params={'courier': courier})
        duration = time.perf_counter() - start_time
        return df, duration
    except Exception as e:
        st.error(f"Failed to execute courier slice query: {e}")
        return pd.DataFrame(), 0.0

