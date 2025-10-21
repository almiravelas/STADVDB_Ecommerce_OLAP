import streamlit as st
import pandas as pd
from utils.db_connection import get_warehouse_engine
from queries.product_queries import get_product_data
from utils.charts import create_bar_chart # Assuming this utility exists

@st.cache_data(ttl=600)
def load_product_data(_engine):
    # This function returns (df, duration)
    return get_product_data(_engine)

def show_product_view(engine):
    st.title("Product Performance Analytics 🛍️")

    # Assuming get_product_data() joins dim_product with a sales fact table
    # and the resulting DataFrame has columns: 'Name', 'Category', 'Price', 'total_sales'
    
    # --- FIX: Unpack the (df, duration) tuple ---
    df, duration = load_product_data(engine)
    # --- END FIX ---

    st.dataframe(df.head()) # This will work now

    if df.empty:
        st.warning("No product data available.")
        return

    # Two-column layout: Filters on the left, results on the right
    left_col, right_col = st.columns([1, 3])

    # --- FILTERS (for Slice and Dice) ---
    with left_col:
        st.subheader("Filters")
        
        # --- (Optional) Add the duration caption for consistency ---
        st.caption(f"Data load time: {duration:.4f} seconds")
        # ---
        
        # Filter by Product Category using the 'Category' column
        categories = sorted(df["category"].unique())
        category_sel = st.multiselect("category", categories, default=categories)
        
        # Filter by a price range using the 'Price' column
        min_price, max_price = float(df["price"].min()), float(df["price"].max())
        price_range = st.slider(
            "Price Range", 
            min_value=min_price, 
            max_value=max_price, 
            value=(min_price, max_price)
        )
        
        # --- GRANULARITY CONTROL (for Roll-up and Drill-down) ---
        group_by = st.radio(
            "Group By", 
            ["product_name", "category"], # Removed "Brand"
            horizontal=False
        )

    # --- DATA PROCESSING AND DISPLAY ---
    with right_col:
        # Map user-friendly group_by names to actual DataFrame column names
        group_col = {
            "product_name": "product_name",
            "category": "category",
        }[group_by]

        # Apply all selected filters to the DataFrame (Dice Operation)
        filtered_df = df[
            (df["category"].isin(category_sel)) &
            (df["price"].between(price_range[0], price_range[1]))
        ]

        # Aggregate the data based on the user's "Group By" selection
        # We assume 'total_sales' is the name of the sales measure from your query
        agg = filtered_df.groupby(group_col)["total_sales"].sum().reset_index()
        agg = agg.sort_values(by="total_sales", ascending=False)

        # --- ANALYTICAL REPORTS ---
        st.subheader("Key Metrics")
        if not agg.empty:
            best, worst = agg.iloc[0], agg.iloc[-1]
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            # Use 'Name' column to count unique products
            metric_col1.metric("Total Products", len(filtered_df["product_name"].unique()))
            metric_col2.metric("Top Performer", best[group_col])
            metric_col3.metric("Lowest Performer", worst[group_col])
        else:
            st.info("No data available for the current filter selections.")

        # --- CHART VISUALIZATION ---
        st.subheader(f"Total Sales by {group_by}")
        st.bar_chart(agg.set_index(group_col)["total_sales"])   # 🆕 simpler, faster

        # --- RAW DATA VIEW ---
        st.subheader("Data View")
        st.dataframe(filtered_df, use_container_width=True, height=400)