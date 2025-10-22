import streamlit as st
# --- MODIFICATION: Remove Altair, import chart functions ---
from utils.charts import create_bar_chart, create_line_chart
# --- END MODIFICATION ---
from queries.sales_queries import (
    get_sales_per_month,
    get_sales_per_year,
    get_sales_by_day_of_week,
    get_sales_weekend_vs_weekday,
    get_daily_sales_trend
)
# --- MODIFICATION: Import time module ---
import time
# --- END MODIFICATION ---

# --- MODIFICATION: Remove SUMMER_PALETTE ---
# (Palette is now controlled by the "seaborn" template in charts.py)
# --- END MODIFICATION ---

def show_date_view(engine):
    st.title("📆 Date-Based Sales Analysis")
    st.caption("Explore how sales vary across time — by day, month, and year.")

    # --- MODIFICATION: Add performance tracking dictionary ---
    perf_metrics = {}
    # --- END MODIFICATION ---

    # Load all OLAP date queries
    with st.spinner("Loading time-based analytics..."):
        # --- MODIFICATION: Time each query ---
        start = time.perf_counter()
        df_month = get_sales_per_month(engine)
        perf_metrics["Sales per Month"] = f"{time.perf_counter() - start:.4f} s"

        start = time.perf_counter()
        df_year = get_sales_per_year(engine)
        perf_metrics["Sales per Year"] = f"{time.perf_counter() - start:.4f} s"

        start = time.perf_counter()
        df_day = get_sales_by_day_of_week(engine)
        perf_metrics["Day of Week"] = f"{time.perf_counter() - start:.4f} s"

        start = time.perf_counter()
        df_weekend = get_sales_weekend_vs_weekday(engine)
        perf_metrics["Weekend/Weekday"] = f"{time.perf_counter() - start:.4f} s"

        start = time.perf_counter()
        df_trend = get_daily_sales_trend(engine)
        perf_metrics["Daily Trend"] = f"{time.perf_counter() - start:.4f} s"
        # --- END MODIFICATION ---

    # --- SALES PER YEAR ---
    st.subheader("📈 Sales per Year")
    if not df_year.empty:
        # --- MODIFICATION: Use create_bar_chart ---
        chart = create_bar_chart(
            df_year, 
            x_axis='year', 
            y_axis='total_sales', 
            title='Sales per Year'
        )
        st.plotly_chart(chart, use_container_width=True)
        # --- END MODIFICATION ---
    else:
        st.warning("No yearly sales data available.")

    # --- SALES PER MONTH ---
    st.subheader("🗓️ Sales per Month")
    if not df_month.empty:
        # --- MODIFICATION: Use create_bar_chart with color grouping ---
        chart = create_bar_chart(
            df_month, 
            x_axis='month_name', 
            y_axis='total_sales', 
            title='Sales per Month', 
            color='year' # <-- This creates the grouped bars
        )
        st.plotly_chart(chart, use_container_width=True)
        # --- END MODIFICATION ---
    else:
        st.warning("No monthly sales data available.")

    # --- DAILY SALES TREND ---
    st.subheader("📆 Daily Sales Trend")
    if not df_trend.empty:
        # --- MODIFICATION: Use create_line_chart ---
        chart = create_line_chart(
            df_trend, 
            x_axis='full_date', 
            y_axis='total_sales', 
            title='Daily Sales Trend'
        )
        st.plotly_chart(chart, use_container_width=True)
        # --- END MODIFICATION ---
    else:
        st.warning("No daily trend data available.")

    # --- SALES BY DAY OF WEEK ---
    st.subheader("📅 Sales by Day of the Week")
    if not df_day.empty:
        # --- MODIFICATION: Use create_bar_chart ---
        chart = create_bar_chart(
            df_day,
            x_axis='day_name',
            y_axis='total_sales',
            title='Sales by Day of the Week'
        )
        st.plotly_chart(chart, use_container_width=True)
        # --- END MODIFICATION ---
    else:
        st.warning("No weekday sales data available.")

    # --- WEEKEND VS WEEKDAY ---
    st.subheader("🧭 Weekend vs Weekday Sales")
    if not df_weekend.empty:
        # --- MODIFICATION: Use create_bar_chart ---
        chart = create_bar_chart(
            df_weekend,
            x_axis='is_weekend',
            y_axis='total_sales',
            title='Weekend vs Weekday Sales'
        )
        st.plotly_chart(chart, use_container_width=True)
        # --- END MODIFICATION ---
    else:
        st.warning("No weekend comparison data available.")

    # --- MODIFICATION: Display performance metrics ---
    st.subheader("Query Performance")
    with st.expander("Show Query Execution Times ⏱️"):
        st.json(perf_metrics)
    # --- END MODIFICATION ---