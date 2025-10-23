"""
EXPLAIN ANALYZE queries for performance testing and optimization
"""
import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
from sqlalchemy import text
import time
import json


def explain_query(engine: Engine, query: str, params: tuple = None, use_analyze: bool = True) -> tuple[dict, float]:
    """
    Run EXPLAIN or EXPLAIN ANALYZE on a query
    Returns parsed explanation and execution time
    """
    if engine is None:
        return {}, 0.0
    
    # Determine database type
    db_type = engine.dialect.name
    
    try:
        start_time = time.perf_counter()
        
        if db_type == "mysql":
            # MySQL supports EXPLAIN ANALYZE (MySQL 8.0.18+) or EXPLAIN FORMAT=JSON
            if use_analyze:
                explain_query_str = f"EXPLAIN ANALYZE {query}"
            else:
                explain_query_str = f"EXPLAIN FORMAT=JSON {query}"
            
            with engine.connect() as conn:
                result = conn.execute(text(explain_query_str), params or {})
                duration = time.perf_counter() - start_time
                
                if use_analyze:
                    # EXPLAIN ANALYZE returns a string
                    explain_output = result.fetchone()[0]
                    return {"type": "analyze_text", "output": explain_output}, duration
                else:
                    # EXPLAIN FORMAT=JSON returns JSON
                    json_output = result.fetchone()[0]
                    parsed = json.loads(json_output)
                    return {"type": "json", "output": parsed}, duration
                    
        elif db_type == "sqlite":
            # SQLite uses EXPLAIN QUERY PLAN
            explain_query_str = f"EXPLAIN QUERY PLAN {query}"
            
            with engine.connect() as conn:
                result = pd.read_sql(text(explain_query_str), conn, params=params or {})
                duration = time.perf_counter() - start_time
                return {"type": "dataframe", "output": result}, duration
                
        else:
            # PostgreSQL and others
            explain_query_str = f"EXPLAIN (FORMAT JSON, ANALYZE {use_analyze}) {query}"
            
            with engine.connect() as conn:
                result = conn.execute(text(explain_query_str), params or {})
                duration = time.perf_counter() - start_time
                json_output = result.fetchone()[0]
                return {"type": "json", "output": json_output}, duration
                
    except Exception as e:
        st.error(f"Failed to execute EXPLAIN: {e}")
        return {"type": "error", "output": str(e)}, 0.0


def get_test_queries() -> dict:
    """
    Return a dictionary of test queries for EXPLAIN ANALYZE
    """
    queries = {
        "Slice by Category (Electronics)": {
            "query": """
                SELECT 
                    dd.year,
                    dd.month_name,
                    dp.category,
                    dp.product_name,
                    du.city,
                    SUM(fs.sales_amount) AS total_sales,
                    SUM(fs.quantity) AS total_quantity,
                    COUNT(DISTINCT fs.order_number) AS total_orders
                FROM fact_sales fs
                JOIN dim_date dd ON fs.date_key = dd.date_key
                JOIN dim_product dp ON fs.product_key = dp.product_key
                JOIN dim_user du ON fs.customer_key = du.user_key
                WHERE dp.category = :category
                GROUP BY dd.year, dd.month_name, dp.category, dp.product_name, du.city
                ORDER BY total_sales DESC
                LIMIT 100;
            """,
            "params": {"category": "Electronics"},
            "description": "Query with WHERE filter on category, multiple JOINs, GROUP BY, and COUNT(DISTINCT)"
        },
        
        "Slice by Year (2024)": {
            "query": """
                SELECT 
                    dd.year,
                    dd.month_name,
                    dp.category,
                    du.city,
                    SUM(fs.sales_amount) AS total_sales,
                    SUM(fs.quantity) AS total_quantity,
                    COUNT(DISTINCT fs.order_number) AS total_orders
                FROM fact_sales fs
                JOIN dim_date dd ON fs.date_key = dd.date_key
                JOIN dim_product dp ON fs.product_key = dp.product_key
                JOIN dim_user du ON fs.customer_key = du.user_key
                WHERE dd.year = :year
                GROUP BY dd.year, dd.month_name, dp.category, du.city
                ORDER BY total_sales DESC
                LIMIT 100;
            """,
            "params": {"year": 2024},
            "description": "Query with date filter - tests index on date_key"
        },
        
    "Slice by Courier (FEDEX)": {
            "query": """
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
                    SUM(fs.sales_amount)/NULLIF(COUNT(DISTINCT fs.order_number),0) AS avg_order_value
                FROM fact_sales fs
                JOIN dim_rider dr ON fs.rider_key = dr.rider_key
                JOIN dim_date dd ON fs.date_key = dd.date_key
                JOIN dim_product dp ON fs.product_key = dp.product_key
                JOIN dim_user du ON fs.customer_key = du.user_key
                WHERE dr.courier_name = :courier
                GROUP BY dr.courier_name, dd.year, dd.month_name, dp.category, du.city, dr.vehicleType
                ORDER BY dd.year, dd.month_name, total_sales DESC
                LIMIT 100;
            """,
            "params": {"courier": "FEDEX"},
            "description": "Query with rider dimension join - tests rider_key index using FEDEX courier"
        },
        
        "Roll-up by Year": {
            "query": """
                SELECT 
                    dd.year,
                    SUM(fs.sales_amount) AS total_sales,
                    SUM(fs.quantity) AS total_quantity,
                    COUNT(DISTINCT fs.order_number) AS total_orders,
                    SUM(fs.sales_amount) / NULLIF(COUNT(DISTINCT fs.order_number), 0) AS avg_order_value
                FROM fact_sales fs
                JOIN dim_date dd ON fs.date_key = dd.date_key
                GROUP BY dd.year
                ORDER BY dd.year;
            """,
            "params": {},
            "description": "Simple aggregation by year - baseline performance"
        },
        
        "Dice (Multi-filter)": {
            "query": """
                SELECT 
                    dd.year,
                    dd.month_name,
                    dp.category,
                    du.city,
                    SUM(fs.sales_amount) AS total_sales,
                    SUM(fs.quantity) AS total_quantity,
                    COUNT(DISTINCT fs.order_number) AS total_orders
                FROM fact_sales fs
                JOIN dim_date dd ON fs.date_key = dd.date_key
                JOIN dim_product dp ON fs.product_key = dp.product_key
                JOIN dim_user du ON fs.customer_key = du.user_key
                WHERE dd.year = :year
                  AND dp.category = :category
                  AND du.city = :city
                GROUP BY dd.year, dd.month_name, dp.category, du.city
                ORDER BY total_sales DESC;
            """,
            "params": {"year": 2024, "category": "Electronics", "city": "Manila"},
            "description": "Multiple WHERE filters - tests compound index effectiveness"
        },
        
        "Optimized: Pre-aggregated Orders": {
            "query": """
                WITH order_agg AS (
                    SELECT 
                        order_number, 
                        date_key, 
                        customer_key, 
                        product_key,
                        SUM(sales_amount) AS order_sales,
                        SUM(quantity) AS order_qty
                    FROM fact_sales
                    WHERE date_key IN (
                        SELECT date_key FROM dim_date WHERE year = :year
                    )
                    GROUP BY order_number, date_key, customer_key, product_key
                )
                SELECT 
                    dd.year,
                    dd.month_name,
                    dp.category,
                    du.city,
                    SUM(oa.order_sales) AS total_sales,
                    SUM(oa.order_qty) AS total_quantity,
                    COUNT(*) AS total_orders
                FROM order_agg oa
                JOIN dim_date dd ON oa.date_key = dd.date_key
                JOIN dim_product dp ON oa.product_key = dp.product_key
                JOIN dim_user du ON oa.customer_key = du.user_key
                GROUP BY dd.year, dd.month_name, dp.category, du.city
                ORDER BY total_sales DESC
                LIMIT 100;
            """,
            "params": {"year": 2024},
            "description": "CTE with pre-aggregation to eliminate COUNT(DISTINCT) - optimized version"
        }
    }
    
    return queries


def get_index_recommendations() -> list:
    """
    Return list of recommended indexes
    """
    return [
        {
            "table": "fact_sales",
            "index_name": "ix_fs_date_key",
            "columns": ["date_key"],
            "sql": "CREATE INDEX ix_fs_date_key ON fact_sales(date_key);",
            "reason": "Improves JOIN performance with dim_date and WHERE filters on year/month"
        },
        {
            "table": "fact_sales",
            "index_name": "ix_fs_product_key",
            "columns": ["product_key"],
            "sql": "CREATE INDEX ix_fs_product_key ON fact_sales(product_key);",
            "reason": "Improves JOIN performance with dim_product"
        },
        {
            "table": "fact_sales",
            "index_name": "ix_fs_customer_key",
            "columns": ["customer_key"],
            "sql": "CREATE INDEX ix_fs_customer_key ON fact_sales(customer_key);",
            "reason": "Improves JOIN performance with dim_user"
        },
        {
            "table": "fact_sales",
            "index_name": "ix_fs_rider_key",
            "columns": ["rider_key"],
            "sql": "CREATE INDEX ix_fs_rider_key ON fact_sales(rider_key);",
            "reason": "Improves JOIN performance with dim_rider"
        },
        {
            "table": "fact_sales",
            "index_name": "ix_fs_order_number",
            "columns": ["order_number"],
            "sql": "CREATE INDEX ix_fs_order_number ON fact_sales(order_number);",
            "reason": "Speeds up COUNT(DISTINCT order_number) operations"
        },
        {
            "table": "dim_product",
            "index_name": "ix_dp_category",
            "columns": ["category"],
            "sql": "CREATE INDEX ix_dp_category ON dim_product(category);",
            "reason": "Improves WHERE dp.category = ? filter performance"
        },
        {
            "table": "dim_rider",
            "index_name": "ix_dr_courier",
            "columns": ["courier_name"],
            "sql": "CREATE INDEX ix_dr_courier ON dim_rider(courier_name);",
            "reason": "Improves WHERE dr.courier_name = ? filter performance"
        },
        {
            "table": "dim_user",
            "index_name": "ix_du_city",
            "columns": ["city"],
            "sql": "CREATE INDEX ix_du_city ON dim_user(city);",
            "reason": "Improves WHERE du.city = ? filter performance"
        },
        {
            "table": "fact_sales",
            "index_name": "ix_fs_composite_date_product",
            "columns": ["date_key", "product_key"],
            "sql": "CREATE INDEX ix_fs_composite_date_product ON fact_sales(date_key, product_key);",
            "reason": "Composite index for queries filtering by both date and product"
        }
    ]
