import streamlit as st
import pandas as pd
from utils.db_connection import get_warehouse_engine
from queries.product_queries import get_product_data
from utils.charts import create_bar_chart  # Assuming this utility exists

@st.cache_data(ttl=600)
def load_product_data(_engine): 
    """Load product data from the database."""
    # This function is assumed to return (df, duration)
    return get_product_data(_engine)

def show_product_view(engine):
    st.title("Product Performance Analytics 🛍️")

    # Load product data
    df, duration = load_product_data(engine)

    if df.empty:
        st.warning("No product data available.")
        return
    
    # Two-column layout: Filters on the left, results on the right
    left_col, right_col = st.columns([1, 3])

    with left_col:
        st.subheader("Filters")
        st.caption(f"Data load time: {duration:.4f} seconds")

        # Filter by Product Category
        categories = sorted(df["category"].unique())
        category_sel = st.multiselect("Category", categories, default=categories)

        # Filter by Price Range
        min_price, max_price = float(df["price"].min()), float(df["price"].max())
        
        # Add fix for slider in case min == max
        if min_price == max_price:
            max_price += 1.0 
            
        price_range = st.slider(
            "Price Range", 
            min_value=min_price, 
            max_value=max_price, 
            value=(min_price, max_price)
        )

        # Granularity Control
        group_by = st.radio("Group By", ["product_name", "category"], horizontal=False)

    with right_col:
        # Apply filters (Slice & Dice)
        filtered_df = df[
            (df["category"].isin(category_sel)) &
            (df["price"].between(price_range[0], price_range[1]))
        ]

        # Aggregate data (Roll-up / Drill-down)
        agg = filtered_df.groupby(group_by)["total_sales"].sum().reset_index()
        agg = agg.sort_values(by="total_sales", ascending=False)

        # Display Key Metrics
        st.subheader("Key Metrics")
        if not agg.empty:
            best, worst = agg.iloc[0], agg.iloc[-1]
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            metric_col1.metric("Total Products", len(filtered_df["product_name"].unique()))
            metric_col2.metric("Top Performer", best[group_by])
            metric_col3.metric("Lowest Performer", worst[group_by])
        else:
            st.info("No data available for the current filter selections.")

        # Chart Visualization
        st.subheader(f"Total Sales by {group_by}")
        st.bar_chart(agg, x=group_by, y="total_sales", color="#FB5533")

        # Raw Data View
        st.subheader("Top Sales Data View")
        
        if group_by == "product_name":
          
            sorted_view_df = filtered_df.sort_values(by="total_sales", ascending=False)
            st.dataframe(sorted_view_df, use_container_width=True, height=400)

        else:
           
            st.dataframe(agg, use_container_width=True, height=400)