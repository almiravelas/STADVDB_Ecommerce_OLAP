import streamlit as st
import pandas as pd
from utils.db_connection import get_warehouse_engine
from queries.rider_queries import get_sales_with_rider_details
from utils.charts import create_bar_chart

def show_rider_view():
    st.title("Rider Performance Analytics")

    engine = get_warehouse_engine()
    df = get_sales_with_rider_details(engine)

    if df.empty:
        st.warning("No rider data available.")
        return

    # Work in progress yung design 
    left_col, right_col = st.columns([1, 3])

    # FILTERS
    with left_col:
        st.subheader("Filter")
        
        couriers = sorted(df["courier_name"].unique())
        courier_sel = st.multiselect("Courier", couriers, default=couriers)

        vehicles = sorted(df["vehicleType"].unique())
        vehicle_sel = st.multiselect("Vehicle Type", vehicles, default=vehicles)
        
        genders = sorted(df["gender"].unique())
        gender_sel = st.multiselect("Gender", genders, default=genders)
        
        min_age, max_age = int(df["age"].min()), int(df["age"].max())
        age_range = st.slider("Age Range", min_value=min_age, max_value=max_age, value=(min_age, max_age))

        group_by = st.radio("Group By", ["Rider Name", "Courier Name", "Vehicle Type", "Gender"], horizontal=False)
    
    with right_col:
        group_col = {
            "Rider Name": "rider_name",
            "Courier Name": "courier_name",
            "Vehicle Type": "vehicleType",
            "Gender": "gender",
        }[group_by]

        # Filters
        filtered_df = df[
            (df["courier_name"].isin(courier_sel)) &
            (df["vehicleType"].isin(vehicle_sel)) &
            (df["gender"].isin(gender_sel)) &
            (df["age"].between(age_range[0], age_range[1]))
        ]

        # aggregation
        agg = filtered_df.groupby(group_col)["sales_amount"].sum().reset_index()
        agg = agg.sort_values(by="sales_amount", ascending=False)

        # metrics
        st.subheader("Key Metrics")
        if not agg.empty:
            best, worst = agg.iloc[0], agg.iloc[-1]
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            metric_col1.metric("Total Riders", len(filtered_df["rider_name"].unique()))
            metric_col2.metric("Top Performer", best[group_col])
            metric_col3.metric("Lowest Performer", worst[group_col])
        else:
            st.info("No data available for current filters.")

        # chart
        st.subheader(f"Total Sales by {group_by}")
        chart = create_bar_chart(agg, group_col, "sales_amount", f"Sales by {group_by}")
        if chart:
            st.plotly_chart(chart, use_container_width=True)

        # raw Data
        st.subheader("Data View")
        st.dataframe(filtered_df, use_container_width=True, height=400)