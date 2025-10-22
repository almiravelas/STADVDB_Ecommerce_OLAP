import streamlit as st
# --- MODIFICATION: Import time module ---
import time
# --- END MODIFICATION ---
from utils.db_connection import get_warehouse_engine
from queries.user_queries import get_user_data, get_distinct_user_attributes
import pandas as pd
# --- MODIFICATION: Remove px, import chart function ---
from utils.charts import create_bar_chart
# --- END MODIFICATION ---
from views.icons import _inject_icon_css, _icon

# --- MODIFICATION: Remove SUMMER_PALETTE ---
# (Palette is now controlled by the "seaborn" template in charts.py)
# --- END MODIFICATION ---

def show_user_view(engine):
    _inject_icon_css()
    _icon("User Demographics & Behavior Analysis", "user", is_title=True)

    left_col, right_col = st.columns([1, 3])

    # --- Filters ---
    with left_col:
        with st.container(border=True):
            _icon("Filters", "filter")
            
            # --- MODIFICATION: Time attribute query ---
            start_attr = time.perf_counter()
            attributes = get_distinct_user_attributes(engine)
            end_attr = time.perf_counter()
            # --- END MODIFICATION ---

            with st.expander("Location Filters", expanded=True):
                selected_continents = st.multiselect("Continent", options=attributes.get("continents", []), key="user_continents")
                selected_countries = st.multiselect("Country", options=attributes.get("countries", []), key="user_countries")
                selected_cities = st.multiselect("City", options=attributes.get("cities", []), key="user_cities")

            with st.expander("Demographic Filters", expanded=True):
                selected_genders = st.multiselect("Gender", options=attributes.get("genders", []), key="user_genders")

            # --- MODIFICATION: Display attribute query time ---
            st.caption(f"Filters loaded in {end_attr - start_attr:.4f}s")
            # --- END MODIFICATION ---

    # --- OPTIMIZATION: Pass ALL filters to the data query function ---

    # --- MODIFICATION: Time main data query ---
    with st.spinner("Loading user data based on filters..."):
        start_data = time.perf_counter()
        df = get_user_data(
            engine, selected_continents, selected_countries, selected_cities, selected_genders
        )
        end_data = time.perf_counter()
        data_load_time = end_data - start_data
    # --- END MODIFICATION ---

    # --- Main content ---
    with right_col:
        
        # --- MODIFICATION: Display main query time ---
        st.caption(f"Data query complete in {data_load_time:.4f} seconds.")
        # --- END MODIFICATION ---
        
        if df.empty:
            st.warning("No data found for selected filters.")
            return

        # KPIs
        with st.container(border=True):
            _icon("Key Metrics", "metrics")
            total_sales = df["sales_amount"].sum()
            unique_users = df["user_key"].nunique()
            
            # --- OPTIMIZATION APPLIED HERE ---
            # We now sum the pre-aggregated order counts from the new query
            total_orders = df["total_orders"].sum()

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
                # --- MODIFICATION: Use create_bar_chart ---
                chart_cont = create_bar_chart(
                    cont, 
                    x_axis="continent", 
                    y_axis="sales_amount", 
                    title="Total Sales by Continent"
                )
                st.plotly_chart(chart_cont, use_container_width=True)
                # --- END MODIFICATION ---

            st.markdown("##### Total Sales by Country")
            country = (
                df.groupby("country")["sales_amount"]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )
            # --- MODIFICATION: Use create_bar_chart ---
            chart_country = create_bar_chart(
                country, 
                x_axis="country", 
                y_axis="sales_amount", 
                title="Total Sales by Country"
            )
            st.plotly_chart(chart_country, use_container_width=True)
            # --- END MODIFICATION ---

        # Aggregated Summary (Binned)
        with st.container(border=True):
            with st.expander("Aggregated Summary (Binned)"):
                # Make sure bin_level options are valid
                valid_bins = [col for col in ["continent", "country", "city"] if col in df.columns]
                if valid_bins:
                    bin_level = st.selectbox("Group data by:", valid_bins, key="user_bin_level")
                    summary = (
                        df.groupby(bin_level)
                        # --- OPTIMIZATION NOTE ---
                        # We also aggregate total_orders here for a richer summary
                        .agg(users=("user_key", "nunique"), 
                             total_sales=("sales_amount", "sum"),
                             total_orders=("total_orders", "sum")
                            )
                        .reset_index()
                        .sort_values("total_sales", ascending=False)
                    )
                    st.dataframe(summary, use_container_width=True)
                else:
                    st.warning("No valid columns available for grouping.")


        # Raw sample (safe display)
        with st.container(border=True):
            
            # --- OPTIMIZATION APPLIED HERE ---
            # Updated text to reflect aggregated data
            with st.expander("Sample of Filtered User-Level Data"):
                st.info("Showing random sample of up to 1,000 aggregated user records.")
                st.dataframe(df.sample(n=min(1000, len(df)), random_state=42), use_container_width=True)