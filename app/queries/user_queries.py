import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
from sqlalchemy.sql import text

@st.cache_data(ttl=600)
def get_user_data(
    _engine: Engine, continents=None, countries=None, cities=None, genders=None
) -> pd.DataFrame:
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

    if continents:
        where_clauses.append("du.continent IN :continents")
        params["continents"] = tuple(continents)
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
        # Fallback in case column doesn't exist (though it should)
        if 'continent' not in df.columns:
            df['continent'] = 'Unknown'
        return df
    except Exception as e:
        st.error(f"⚠️ Error fetching user data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=600)
def get_distinct_user_attributes(_engine: Engine) -> dict:
    """
    --- OPTIMIZATION: Fetches all distinct values for filters in a single query ---
    """
    if _engine is None:
        return {"continents": [], "countries": [], "cities": [], "genders": []}

    query = """
    SELECT 'continent' as attr_type, continent as value FROM dim_user WHERE continent IS NOT NULL GROUP BY continent
    UNION ALL
    SELECT 'country' as attr_type, country as value FROM dim_user WHERE country IS NOT NULL GROUP BY country
    UNION ALL
    SELECT 'city' as attr_type, city as value FROM dim_user WHERE city IS NOT NULL GROUP BY city
    UNION ALL
    SELECT 'gender' as attr_type, gender as value FROM dim_user WHERE gender IS NOT NULL GROUP BY gender
    ORDER BY attr_type, value
    """
    try:
        df = pd.read_sql(text(query), _engine)

        # Process the single DataFrame into the required dict format
        return {
            "continents": df[df['attr_type'] == 'continent']['value'].tolist(),
            "countries": df[df['attr_type'] == 'country']['value'].tolist(),
            "cities": df[df['attr_type'] == 'city']['value'].tolist(),
            "genders": df[df['attr_type'] == 'gender']['value'].tolist()
        }

    except Exception as e:
        st.error(f"Could not fetch user attributes: {e}")
        return {"continents": [], "countries": [], "cities": [], "genders": []}