import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
from sqlalchemy.sql import text

@st.cache_data(ttl=600)
def get_user_data(_engine: Engine, countries=None, cities=None, genders=None) -> pd.DataFrame:
    """Loads user-level OLAP data with continent support."""
    if _engine is None:
        return pd.DataFrame()

    query = """
    SELECT
        fs.sales_amount,
        fs.order_number,
        du.user_key,
        du.username,
        du.country,
        du.city,
        du.gender,
        du.continent,
        dd.year,
        dd.month_name
    FROM fact_sales fs
    JOIN dim_user du ON fs.customer_key = du.user_key
    JOIN dim_date dd ON fs.date_key = dd.date_key
    """

    where_clauses, params = [], {}

    if countries:
        where_clauses.append("du.country IN :countries")
        params["countries"] = tuple(countries)
    if cities:
        where_clauses.append("du.city IN :cities")
        params["cities"] = tuple(cities)
    if genders:
        where_clauses.append("du.gender IN :genders")
        params["genders"] = tuple(genders)

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    try:
        df = pd.read_sql(text(query), _engine, params=params)
        if 'continent' not in df.columns:
            df['continent'] = 'Unknown'
        return df
    except Exception as e:
        st.error(f"⚠️ Error fetching user data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_distinct_user_attributes(_engine: Engine) -> dict:
    """Fetches distinct values for filters."""
    if _engine is None:
        return {"continents": [], "countries": [], "cities": [], "genders": []}

    try:
        continents = pd.read_sql(
            "SELECT DISTINCT continent FROM dim_user WHERE continent IS NOT NULL ORDER BY continent", _engine
        )["continent"].tolist()

        countries = pd.read_sql(
            "SELECT DISTINCT country FROM dim_user WHERE country IS NOT NULL ORDER BY country", _engine
        )["country"].tolist()

        cities = pd.read_sql(
            "SELECT DISTINCT city FROM dim_user WHERE city IS NOT NULL ORDER BY city", _engine
        )["city"].tolist()

        genders = pd.read_sql(
            "SELECT DISTINCT gender FROM dim_user WHERE gender IS NOT NULL ORDER BY gender", _engine
        )["gender"].tolist()

        return {
            "continents": continents,
            "countries": countries,
            "cities": cities,
            "genders": genders
        }

    except Exception as e:
        st.error(f"Could not fetch user attributes: {e}")
        return {"continents": [], "countries": [], "cities": [], "genders": []}
