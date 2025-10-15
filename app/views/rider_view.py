import streamlit as st
import pandas as pd
from utils.db_connection import get_warehouse_engine
from queries.rider_queries import get_sales_with_rider_details
from utils.charts import create_bar_chart

@st.cache_data(ttl=600)
def load_rider_data(_engine):
    """Loads rider and sales data from the database, caching the result."""
    return get_sales_with_rider_details(_engine)

def show_rider_view(engine):
    """Renders the Rider Performance Analytics tab."""
    st.title("Rider Performance Analytics 🛵")

    df = load_rider_data(engine)

    if df.empty:
        st.warning("No rider data available.")
        return

    # --- Main Layout: Filters on the left, Visualizations on the right ---
    left_col, right_col = st.columns([1, 3])

    # --- FILTERS ---
    with left_col:
        st.subheader("Filters")
        
        # Date Filters
        years = sorted(df["year"].unique())
        year_sel = st.multiselect("Year", years, default=years)

        months = sorted(df["month_name"].unique())
        month_sel = st.multiselect("Month", months, default=months)
        
        # Rider Attribute Filters
        couriers = sorted(df["courier_name"].unique())
        courier_sel = st.multiselect("Courier", couriers, default=couriers)

        vehicles = sorted(df["vehicleType"].unique())
        vehicle_sel = st.multiselect("Vehicle Type", vehicles, default=vehicles)
        
        genders = sorted(df["gender"].unique())
        gender_sel = st.multiselect("Gender", genders, default=genders)
        
        min_age, max_age = int(df["age"].min()), int(df["age"].max())
        age_range = st.slider("Age Range", min_value=min_age, max_value=max_age, value=(min_age, max_age))

        # --- OLAP & DISPLAY OPTIONS ---
        st.subheader("Analysis Options")
        group_by = st.radio(
            "Group By (Rows)", 
            ["Courier Name", "Vehicle Type", "Gender", "Rider Name"], 
            horizontal=False
        )
        
        display_mode = st.radio(
            "View As",
            ["Summary Chart", "Pivot Table"],
            horizontal=True,
            help="Choose 'Summary Chart' for an overview or 'Pivot Table' for detailed cross-analysis."
        )

        pivot_column_selection = None
        if display_mode == "Pivot Table":
            # Let the user choose what to use for the pivot columns
            pivot_column_options = ["year", "vehicleType", "gender"]
            pivot_column_selection = st.selectbox("Pivot On (Columns)", pivot_column_options)

    # --- DATA PROCESSING & VISUALIZATION ---
    with right_col:
        group_col = {
            "Rider Name": "rider_name",
            "Courier Name": "courier_name",
            "Vehicle Type": "vehicleType",
            "Gender": "gender",
        }[group_by]

        # Apply all selected filters to the DataFrame
        filtered_df = df[
            (df["year"].isin(year_sel)) &
            (df["month_name"].isin(month_sel)) &
            (df["courier_name"].isin(courier_sel)) &
            (df["vehicleType"].isin(vehicle_sel)) &
            (df["gender"].isin(gender_sel)) &
            (df["age"].between(age_range[0], age_range[1]))
        ]
        
        # --- CONDITIONAL DISPLAY LOGIC ---
        if display_mode == "Summary Chart":
            agg = filtered_df.groupby(group_col)["sales_amount"].sum().reset_index()
            agg = agg.sort_values(by="sales_amount", ascending=False)

            # Display Key Metrics
            st.subheader("Key Metrics")
            if not agg.empty:
                best, worst = agg.iloc[0], agg.iloc[-1]
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                metric_col1.metric("Total Riders", len(filtered_df["rider_name"].unique()))
                metric_col2.metric("Top Performer", best[group_col])
                metric_col3.metric("Lowest Performer", worst[group_col])
            else:
                st.info("No data available for the current filter selections.")

            # Display Bar Chart
            st.subheader(f"Top 10 Total Sales by {group_by}")
            chart = create_bar_chart(agg.head(10), group_col, "sales_amount", f"Sales by {group_by}")
            if chart:
                st.plotly_chart(chart, use_container_width=True)

        elif display_mode == "Pivot Table":
            st.subheader(f"Sales Pivot: {group_by} vs. {pivot_column_selection.title()}")

            # Prevent user from selecting the same column for rows and columns
            if group_col == pivot_column_selection:
                st.warning("Group By (Rows) and Pivot On (Columns) cannot be the same. Please select different options.")
            else:
                try:
                    pivot_table = pd.pivot_table(
                        filtered_df,
                        values='sales_amount',        # The measure to aggregate
                        index=group_col,              # The rows of the table
                        columns=pivot_column_selection, # The columns of the table
                        aggfunc='sum',                # The aggregation function
                        fill_value=0                  # Replace empty cells with 0
                    )

                    # Display the formatted pivot table
                    st.dataframe(
                        pivot_table.style.format("₱{:,.2f}"),
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Could not create the pivot table: {e}")

        # --- Raw Data View (Common to both display modes) ---
        st.subheader("Data View")
        
        # Limit the displayed rows to prevent performance issues
        if len(filtered_df) > 1000:
            st.info(f"Displaying the first 1,000 rows out of {len(filtered_df):,} total rows.")
            st.dataframe(filtered_df.head(1000), use_container_width=True, height=400)
        elif filtered_df.empty:
            st.info("No data to display for the current filter selection.")
        else:
            st.dataframe(filtered_df, use_container_width=True, height=400)