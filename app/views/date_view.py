import streamlit as st
from utils.db_connection import get_warehouse_engine
import altair as alt
from queries.sales_queries import (
    get_sales_per_month,
    get_sales_per_year,
    get_sales_by_day_of_week,
    get_sales_weekend_vs_weekday,
    get_daily_sales_trend
)

@st.cache_data(ttl=600)
def show_date_view():
    st.title("Date Dimension Analytics")

    engine = get_warehouse_engine()
    st.title("📆 Date-Based Sales Analysis")
    st.caption("Explore how sales vary across time — by day, month, and year.")

    # Load all OLAP date queries
    with st.spinner("Loading time-based analytics..."):
        df_month = get_sales_per_month(engine)
        df_year = get_sales_per_year(engine)
        df_day = get_sales_by_day_of_week(engine)
        df_weekend = get_sales_weekend_vs_weekday(engine)
        df_trend = get_daily_sales_trend(engine)

    # --- SALES PER YEAR ---
    st.subheader("📈 Sales per Year")
    if not df_year.empty:
        chart = alt.Chart(df_year).mark_bar().encode(
            x='year:O',
            y='total_sales:Q',
            tooltip=['year', 'total_sales']
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("No yearly sales data available.")

    # --- SALES PER MONTH ---
    st.subheader("🗓️ Sales per Month")
    if not df_month.empty:
        chart = alt.Chart(df_month).mark_bar().encode(
            x='month_name:N',
            y='total_sales:Q',
            color='year:N',
            tooltip=['year', 'month_name', 'total_sales']
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("No monthly sales data available.")

    # --- DAILY SALES TREND ---
    st.subheader("📆 Daily Sales Trend")
    if not df_trend.empty:
        chart = alt.Chart(df_trend).mark_line(point=True).encode(
            x='full_date:T',
            y='total_sales:Q',
            tooltip=['full_date', 'total_sales']
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("No daily trend data available.")

    # --- SALES BY DAY OF WEEK ---
    st.subheader("📅 Sales by Day of the Week")
    if not df_day.empty:
        chart = alt.Chart(df_day).mark_bar().encode(
            x=alt.X('day_name:N', sort=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']),
            y='total_sales:Q',
            tooltip=['day_name', 'total_sales']
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("No weekday sales data available.")

    # --- WEEKEND VS WEEKDAY ---
    st.subheader("🧭 Weekend vs Weekday Sales")
    if not df_weekend.empty:
        chart = alt.Chart(df_weekend).mark_bar().encode(
            x=alt.X('is_weekend:N', title='Weekend (Y/N)'),
            y='total_sales:Q',
            tooltip=['is_weekend', 'total_sales']
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("No weekend comparison data available.")