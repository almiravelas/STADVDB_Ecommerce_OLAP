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

    with left_col:
        with st.container(border=True):
            _icon("Filters", "filter")
            attributes = get_distinct_user_attributes(engine)
            
            with st.expander("Location Filters", expanded=True):
                selected_countries = st.multiselect("Country", options=attributes.get("countries", []))
                selected_cities = st.multiselect("City", options=attributes.get("cities", []))

            with st.expander("Demographic Filters", expanded=True):
                selected_genders = st.multiselect("Gender", options=attributes.get("genders", []))

    df = load_user_data(engine, selected_countries, selected_cities, selected_genders)

    with right_col:
        if df.empty:
            st.warning("DATA for the selected filters. Please try a different selection.")
            return

        # --- KPIs ---
        with st.container(border=True):
            _icon("Key Metrics", "metrics")
            total_sales = df['sales_amount'].sum()
            unique_users = df['user_key'].nunique()
            total_orders = df['order_number'].nunique()

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Sales", f"₱{total_sales:,.2f}")
            c2.metric("Unique Customers", f"{unique_users:,}")
            c3.metric("Total Orders", f"{total_orders:,}")

        # --- Visualizations (Roll-up & Drill-down) ---
        with st.container(border=True):
            _icon("Geographic Sales Analysis", "chart")
            st.markdown("##### Total Sales by Country (Roll-up)")
            sales_by_country = df.groupby('country')['sales_amount'].sum().sort_values(ascending=False).reset_index()
            fig_country = px.bar(sales_by_country, x='country', y='sales_amount', labels={'sales_amount': 'Total Sales (PHP)'})
            st.plotly_chart(fig_country, use_container_width=True)

            st.markdown("##### Top 15 Cities by Sales (Drill-down)")
            sales_by_city = df.groupby('city')['sales_amount'].sum().sort_values(ascending=False).head(15).reset_index()
            fig_city = px.bar(sales_by_city, x='city', y='sales_amount', labels={'sales_amount': 'Total Sales (PHP)'})
            st.plotly_chart(fig_city, use_container_width=True)

        # --- Pivot Table ---
        with st.container(border=True):
            _icon("Sales Pivot: Country vs. Gender", "table")
            pivot_table = pd.pivot_table(
                df, 
                values='sales_amount', 
                index='country', 
                columns='gender', 
                aggfunc='sum', 
                fill_value=0,
                margins=True,
                margins_name="Grand Total"
            )
            st.dataframe(pivot_table.style.format("₱{:,.2f}"), use_container_width=True)

        # --- Raw Data Expander ---
        with st.container(border=True):
            with st.expander("View Filtered Raw Data"):
                st.dataframe(df, use_container_width=True)

