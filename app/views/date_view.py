import streamlit as st
import pandas as pd
from utils.db_connection import get_warehouse_engine

@st.cache_data(ttl=600)
def show_date_view(_engine):
    st.title("Date Dimension Analytics")

    engine = get_warehouse_engine()

    # Load the date dimension
    query = "SELECT * FROM dim_date;"
    df = pd.read_sql(query, engine)

    if df.empty:
        st.warning("No date data available.")
        return

    # --- Filters ---
    st.sidebar.header("Filters")

    years = sorted(df["year"].unique())
    year_sel = st.sidebar.multiselect("Year", years, default=years)

    months = sorted(df["month_name"].unique())
    month_sel = st.sidebar.multiselect("Month", months, default=months)

    weekend_sel = st.sidebar.radio("Weekend Filter", ["All", "Weekdays Only", "Weekends Only"])

    # Apply filters
    filtered_df = df[(df["year"].isin(year_sel)) & (df["month_name"].isin(month_sel))]

    if weekend_sel == "Weekdays Only":
        filtered_df = filtered_df[filtered_df["is_weekend"] == "N"]
    elif weekend_sel == "Weekends Only":
        filtered_df = filtered_df[filtered_df["is_weekend"] == "Y"]

    # --- Metrics ---
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Days", len(filtered_df))
    col2.metric("Weekend Days", len(filtered_df[filtered_df["is_weekend"] == "Y"]))
    col3.metric("Weekday Days", len(filtered_df[filtered_df["is_weekend"] == "N"]))

    # --- Monthly Count Chart ---
    st.subheader("Days by Month")
    monthly_counts = filtered_df.groupby(["year", "month_name"]).size().reset_index(name="day_count")
    monthly_counts = monthly_counts.sort_values(by=["year", "month_name"])

    st.bar_chart(monthly_counts.set_index("month_name")["day_count"])

    # --- Raw Data ---
    st.subheader("Data View")
    st.dataframe(filtered_df, use_container_width=True, height=400)
