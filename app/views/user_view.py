import streamlit as st
from utils.db_connection import get_warehouse_engine
from queries.user_queries import get_user_data, get_distinct_user_attributes
import pandas as pd
import plotly.express as px
from views.icons import _inject_icon_css, _icon

@st.cache_data(ttl=600)
def load_user_data(_engine, countries=None, cities=None, genders=None):
    return get_user_data(_engine, countries, cities, genders)

def show_user_view(engine):
    _inject_icon_css()
    _icon("User Demographics & Behavior Analysis", "user", is_title=True)

    left_col, right_col = st.columns([1, 3])

    # --- Filters ---
    with left_col:
        with st.container(border=True):
            _icon("Filters", "filter")
            attributes = get_distinct_user_attributes(engine)

            with st.expander("Location Filters", expanded=True):
                selected_continents = st.multiselect("Continent", options=attributes.get("continents", []))
                selected_countries = st.multiselect("Country", options=attributes.get("countries", []))
                selected_cities = st.multiselect("City", options=attributes.get("cities", []))

            with st.expander("Demographic Filters", expanded=True):
                selected_genders = st.multiselect("Gender", options=attributes.get("genders", []))

    df = load_user_data(engine, selected_countries, selected_cities, selected_genders)

    # Apply continent filter client-side
    if selected_continents and "continent" in df.columns:
        df = df[df["continent"].isin(selected_continents)]

    # --- Main content ---
    with right_col:
        if df.empty:
            st.warning("No data found for selected filters.")
            return

        # KPIs
        with st.container(border=True):
            _icon("Key Metrics", "metrics")
            total_sales = df["sales_amount"].sum()
            unique_users = df["user_key"].nunique()
            total_orders = df["order_number"].nunique()

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Sales", f"₱{total_sales:,.2f}")
            c2.metric("Unique Customers", f"{unique_users:,}")
            c3.metric("Total Orders", f"{total_orders:,}")

        # Charts
        with st.container(border=True):
            _icon("Sales by Geography", "chart")

            if "continent" in df.columns:
                st.markdown("##### Total Sales by Continent")
                cont = (
                    df.groupby("continent")["sales_amount"]
                    .sum()
                    .sort_values(ascending=False)
                    .reset_index()
                )
                st.plotly_chart(
                    px.bar(cont, x="continent", y="sales_amount", labels={"sales_amount": "Total Sales (PHP)"}),
                    use_container_width=True,
                )

            st.markdown("##### Total Sales by Country")
            country = (
                df.groupby("country")["sales_amount"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )
            st.plotly_chart(
                px.bar(country, x="country", y="sales_amount", labels={"sales_amount": "Total Sales (PHP)"}),
                use_container_width=True,
            )

        # Aggregated Summary (Binned)
        with st.container(border=True):
            with st.expander("Aggregated Summary (Binned)"):
                bin_level = st.selectbox("Group data by:", ["continent", "country", "city"])
                summary = (
                    df.groupby(bin_level)
                    .agg(users=("user_key", "nunique"), total_sales=("sales_amount", "sum"))
                    .reset_index()
                    .sort_values("total_sales", ascending=False)
                )
                st.dataframe(summary, use_container_width=True)

        # Raw sample (safe display)
        with st.container(border=True):
            with st.expander("Sample of Filtered Raw Data"):
                st.info("Showing random sample of up to 1,000 rows.")
                st.dataframe(df.sample(n=min(1000, len(df)), random_state=42), use_container_width=True)
