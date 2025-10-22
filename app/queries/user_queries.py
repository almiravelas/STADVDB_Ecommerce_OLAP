import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine
from sqlalchemy.sql import text


@st.cache_data(ttl=600)
def get_user_data(
    _engine: Engine, continents=None, countries=None, cities=None, genders=None
) -> pd.DataFrame:
    """
    --- OPTIMIZED ---
    Loads pre-aggregated user-level OLAP data.
    Instead of pulling raw sales, we GROUP BY the user and their
    attributes to get per-user totals. This dramatically
    reduces the data transferred to Streamlit.
    """
    if _engine is None:
        return pd.DataFrame()

    query = """
    SELECT
        du.user_key,
        du.continent,
        du.country,
        du.city,
        du.gender,
        SUM(fs.sales_amount) AS sales_amount,
        COUNT(DISTINCT fs.order_number) AS total_orders
    FROM fact_sales fs
    JOIN dim_user du ON fs.customer_key = du.user_key
    -- The JOIN to dim_date was removed as its columns (year, month_name)
    -- were not used in the Streamlit view, saving query time.
    """

    where_clauses, params = [], {}

    # --- FIX: Manually unroll list parameters for mysql-connector ---
    # This is necessary because the driver cannot expand tuples for IN clauses.

    if continents:
        # 1. Create a list of unique, named parameters (e.g., [':cont_0', ':cont_1'])
        continent_params = [f":cont_{i}" for i in range(len(continents))]
        # 2. Add them to the WHERE clause (e.g., "du.continent IN (:cont_0, :cont_1)")
        where_clauses.append(f"du.continent IN ({', '.join(continent_params)})")
        # 3. Add each value to the params dict (e.g., {'cont_0': 'Africa', 'cont_1': 'Asia'})
        for param_name, value in zip(continent_params, continents):
            params[param_name.lstrip(':')] = value

    if countries:
        country_params = [f":country_{i}" for i in range(len(countries))]
        where_clauses.append(f"du.country IN ({', '.join(country_params)})")
        for param_name, value in zip(country_params, countries):
            params[param_name.lstrip(':')] = value

    if cities:
        city_params = [f":city_{i}" for i in range(len(cities))]
        where_clauses.append(f"du.city IN ({', '.join(city_params)})")
        for param_name, value in zip(city_params, cities):
            params[param_name.lstrip(':')] = value

    if genders:
        gender_params = [f":gender_{i}" for i in range(len(genders))]
        where_clauses.append(f"du.gender IN ({', '.join(gender_params)})")
        for param_name, value in zip(gender_params, genders):
            params[param_name.lstrip(':')] = value
    # --- END FIX ---

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    # Add the GROUP BY clause to aggregate the data
    query += """
    GROUP BY
        du.user_key,
        du.continent,
        du.country,
        du.city,
        du.gender
    """

    try:
        # This call is now correct, as the query string has the expanded
        # parameters and the params dict has the corresponding values.
        df = pd.read_sql(text(query), _engine, params=params)
        
        # Fallback in case column doesn't exist
        if 'continent' not in df.columns:
            df['continent'] = 'Unknown'
        return df
    except Exception as e:
        st.error(f"⚠️ Error fetching user data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=600)
def get_distinct_user_attributes(_engine: Engine) -> dict:
    """
    (This function is already well-optimized, no change needed)
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