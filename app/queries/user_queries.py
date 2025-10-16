import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
from sqlalchemy.sql import text

@st.cache_data(ttl=600)
def get_user_data(_engine: Engine, countries: list = None, cities: list = None, genders: list = None) -> pd.DataFrame:
    """
    Performs OLAP queries on the user dimension by joining the sales fact
    table with the user dimension table. It allows for slicing and dicing
    based on country, city, and gender.
    """
    if _engine is None:
        return pd.DataFrame()

    # This query joins the sales fact with the user dimension, forming our data cube.
    query = """
    SELECT
        fs.sales_amount,
        fs.order_number,
        du.user_key,
        du.username,
        du.country,
        du.city,
        du.gender,
        dd.year,
        dd.month_name
    FROM fact_sales fs
    JOIN dim_user du ON fs.user_key = du.user_key
    JOIN dim_date dd ON fs.date_key = dd.dateID
    """
    
    # This part dynamically adds filters to the query for slicing and dicing.
    where_clauses = []
    params = {}
    
    if countries:
        where_clauses.append("du.country IN :countries")
        params['countries'] = tuple(countries)
        
    if cities:
        where_clauses.append("du.city IN :cities")
        params['cities'] = tuple(cities)

    if genders:
        where_clauses.append("du.gender IN :genders")
        params['genders'] = tuple(genders)

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    try:
        sql_query = text(query)
        df = pd.read_sql(sql_query, _engine, params=params)
        return df
    except Exception as e:
        st.error(f"⚠️ Error fetching user data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_distinct_user_attributes(_engine: Engine) -> dict:
    """
    Fetches distinct values for filter widgets to populate them dynamically.
    """
    if _engine is None:
        return {"countries": [], "cities": [], "genders": []}
    try:
        countries = pd.read_sql("SELECT DISTINCT country FROM dim_user WHERE country IS NOT NULL ORDER BY country", _engine)['country'].tolist()
        cities = pd.read_sql("SELECT DISTINCT city FROM dim_user WHERE city IS NOT NULL ORDER BY city", _engine)['city'].tolist()
        genders = pd.read_sql("SELECT DISTINCT gender FROM dim_user WHERE gender IS NOT NULL ORDER BY gender", _engine)['gender'].tolist()
        
        return {
            "countries": countries,
            "cities": cities,
            "genders": genders
        }
    except Exception as e:
        st.error(f"Could not fetch filter attributes: {e}")
        return {"countries": [], "cities": [], "genders": []}