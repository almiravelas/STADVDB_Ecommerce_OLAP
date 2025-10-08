import streamlit as st
from utils.db_connection import get_warehouse_engine
from queries.rider_queries import get_sales_with_rider_details
from utils.charts import create_bar_chart
import pandas as pd

# WORK IN PROGRESS 
def show_dashboard():
    st.title("Dashboard")

    engine = get_warehouse_engine()
    if not engine:
        st.stop()

    df = get_sales_with_rider_details(engine)
    if df.empty:
        st.warning("No data found for Rider + Sales join.")
        st.stop()

    total_sales = df["sales_amount"].sum()
    total_orders = df["order_number"].nunique()
    total_riders = df["rider_name"].nunique()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Sales (₱)", f"{total_sales:,.2f}")
    c2.metric("Total Orders", total_orders)
    c3.metric("Active Riders", total_riders)

    agg = df.groupby("courier_name")["sales_amount"].sum().reset_index()
    chart = create_bar_chart(agg, "courier_name", "sales_amount", "Sales by Courier")
    st.plotly_chart(chart, use_container_width=True)
