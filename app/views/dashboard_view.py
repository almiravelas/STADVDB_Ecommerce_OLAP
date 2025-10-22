import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db_connection import get_warehouse_engine  # noqa: F401 (compat)
from queries.rider_queries import get_sales_for_dashboard
# --- MODIFICATION: Import the new function ---
from queries.product_queries import get_dashboard_product_data
# --- END MODIFICATION ---
from utils.charts import create_bar_chart
from views.icons import _inject_icon_css, _icon, ORANGE

def _inject_extra_css():
    st.markdown(
        """
        <style>
          /* Prevent truncation/ellipsis in st.metric values */
          div[data-testid="stMetricValue"] > div {
            overflow: visible !important;
            text-overflow: clip !important;
            white-space: nowrap !important;
          }
          div[data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; }
        </style>
        """,
        unsafe_allow_html=True
    )

# =========================
# QUARTER HELPERS
# =========================
QUARTER_LABELS = ["Q1 (Jan–Mar)", "Q2 (Apr–Jun)", "Q3 (Jul–Sep)", "Q4 (Oct–Dec)"]
MONTH_TO_Q = {
    "January": QUARTER_LABELS[0],
    "February": QUARTER_LABELS[0],
    "March": QUARTER_LABELS[0],
    "April": QUARTER_LABELS[1],
    "May": QUARTER_LABELS[1],
    "June": QUARTER_LABELS[1],
    "July": QUARTER_LABELS[2],
    "August": QUARTER_LABELS[2],
    "September": QUARTER_LABELS[2],
    "October": QUARTER_LABELS[3],
    "November": QUARTER_LABELS[3],
    "December": QUARTER_LABELS[3],
}

def _ensure_quarter(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add month_num, date (YYYY-MM-01), and quarter columns when possible.
    Works with either month_name or month integer columns.
    """
    if df is None or df.empty:
        return df
    out = df.copy()

    # month_num
    if "month_name" in out.columns:
        try:
            out["month_num"] = pd.to_datetime(out["month_name"], format="%B").dt.month
        except Exception:
            month_map = {m: i for i, m in enumerate(
                ["January","February","March","April","May","June","July","August","September","October","November","December"], start=1)}
            out["month_num"] = out["month_name"].map(month_map)
    elif "month" in out.columns:
        out["month_num"] = pd.to_numeric(out["month"], errors="coerce").astype("Int64")
    else:
        out["month_num"] = pd.NA

    # date column for monthly trend (first day of month)
    if "year" in out.columns:
        out["date"] = pd.to_datetime(
            out["year"].astype(str) + "-" + out["month_num"].astype(str) + "-01",
            errors="coerce"
        )

    # quarter column
    if "quarter" not in out.columns:
        if "month_name" in out.columns:
            out["quarter"] = out["month_name"].map(MONTH_TO_Q)
        elif "month_num" in out.columns:
            def _q(m):
                if pd.isna(m): return None
                m = int(m)
                return QUARTER_LABELS[(m-1)//3]
            out["quarter"] = out["month_num"].apply(_q)
        else:
            out["quarter"] = None

    return out

# =========================
# SAFE/FORMAT HELPERS
# =========================
def _format_compact(n):
    """Return 1.2K / 3.4M / 5.6B style strings; '—' for None/NaN/invalid."""
    try:
        if n is None or (isinstance(n, float) and pd.isna(n)):
            return "—"
        n = float(n)
    except Exception:
        return "—"
    a = abs(n)
    if a >= 1e12: return f"{n/1e12:.1f}T"
    if a >= 1e9:  return f"{n/1e9:.1f}B"
    if a >= 1e6:  return f"{n/1e6:.1f}M"
    if a >= 1e3:  return f"{n/1e3:.1f}K"
    return f"{n:,.0f}"

def _center_title(fig, size=16):
    """Center plotly title and hide any color scale."""
    if fig is None:
        return None
    fig.update_layout(
        title={'x': 0.5, 'xanchor': 'center'},
        title_font=dict(size=size),
        coloraxis_showscale=False
    )
    return fig

# =========================
# DATA LOADERS
# =========================
@st.cache_data(ttl=600)
def load_dashboard_data(_engine):
    """
    Loads and preprocesses rider sales data for the dashboard
    using the optimized, order-level pre-aggregated query.
    Returns a tuple (DataFrame, duration).
    """
    # This now calls the *pre-aggregated* query
    df, duration = get_sales_for_dashboard(_engine)
    if not df.empty:
        df = _ensure_quarter(df)
    return df, duration  # Return both

@st.cache_data(ttl=600)
def load_product_preview_data(_engine):
    """
    Loads product sales data for the dashboard preview.
    Uses the new pre-aggregated product query.
    Returns a tuple (DataFrame, duration).
    """
    try:
        # --- MODIFICATION: Call the new dashboard-specific function ---
        df, duration = get_dashboard_product_data(_engine)
        # --- END MODIFICATION ---
    except Exception:
        return pd.DataFrame(), 0.0
        
    if not df.empty:
        df = _ensure_quarter(df)
    return df, duration # Return both

# =========================
# MAIN VIEW
# =========================
def show_dashboard(engine):
    """
    Renders the main dashboard view with quarter filters, title-sized headers,
    flat orange SVG icons, robust metric formatting, and centered chart titles.
    """
    _inject_icon_css()
    _inject_extra_css()   # local patch
    _icon("Main Dashboard", "dashboard", is_title=True)

    left_col, right_col = st.columns([1, 3])

    filter_box = left_col.container(border=True)
    metrics_box = left_col.container(border=True)
    chart_box_1 = right_col.container(border=True)
    chart_box_2 = right_col.container(border=True)

    # Load data (now using the optimized queries)
    df_rider, rider_duration = load_dashboard_data(engine)
    df_product, product_duration = load_product_preview_data(engine)

    if df_rider is None or df_rider.empty:
        st.warning("No sales data available to display on the dashboard.")
        return

    # ---------------- LEFT: FILTERS ----------------
    with filter_box:
        _icon("Time Horizon", "calendar")
        
        st.caption(f"Rider data query: {rider_duration:.4f} s")
        st.caption(f"Product data query: {product_duration:.4f} s")

        years = sorted(df_rider["year"].dropna().unique(), reverse=True)
        year_sel = st.multiselect("Year", years, default=years, key="dash_year_sel")

        quarters_available = [q for q in QUARTER_LABELS if q in set(df_rider["quarter"].dropna().unique())]
        if not quarters_available:
            st.info("No quarter information found; showing all data.")
            quarter_sel = QUARTER_LABELS
        else:
            quarter_sel = st.multiselect("Quarter", quarters_available, default=quarters_available, key="dash_quarter_sel")

    # Apply filters *after* they have been defined
    filtered_df_rider = df_rider[
        (df_rider["year"].isin(year_sel)) &
        (df_rider["quarter"].isin(quarter_sel) if quarter_sel else True)
    ]
    filtered_df_product = df_product[
        (df_product["year"].isin(year_sel)) &
        (df_product["quarter"].isin(quarter_sel) if quarter_sel else True)
    ] if (df_product is not None and not df_product.empty) else pd.DataFrame()


    # ---------------- LEFT: METRICS ----------------
    with metrics_box:
        _icon("Key Metrics", "metrics")

        # This logic still works perfectly with the pre-aggregated order-level data
        if not filtered_df_rider.empty:
            total_sales = filtered_df_rider["sales_amount"].sum() if "sales_amount" in filtered_df_rider.columns else None
            total_orders = (filtered_df_rider["order_number"].nunique()
                            if "order_number" in filtered_df_rider.columns else None)
            
            rider_key_col = "rider_key" if "rider_key" in filtered_df_rider.columns else "rider_name"
            total_riders = (filtered_df_rider[rider_key_col].nunique()
                            if rider_key_col in filtered_df_rider.columns else None)

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Sales", f"₱{_format_compact(total_sales)}")
            c2.metric("Total Orders", _format_compact(total_orders))
            c3.metric("Active Riders", _format_compact(total_riders))

            exact_bits = []
            if total_sales is not None: exact_bits.append(f"₱{total_sales:,.2f}")
            if total_orders is not None: exact_bits.append(f"{int(total_orders):,} orders")
            if total_riders is not None: exact_bits.append(f"{int(total_riders):,} riders")
            if exact_bits:
                st.caption("Exact totals: " + " · ".join(exact_bits))
        else:
            st.info("No data for selected period.")


    # ---------------- RIGHT: VISUALIZATIONS -------------------
    if filtered_df_rider.empty:
        right_col.warning("No data available for the selected date range.")
        return

    with chart_box_1:
        _icon("Sales Trend Over Time", "chart")

        # This aggregation is now much faster as it runs on order-level data
        monthly_sales = (
            filtered_df_rider
            .dropna(subset=["date"])
            .groupby("date", as_index=False)["sales_amount"]
            .sum()
            .sort_values("date")
            .dropna(subset=["sales_amount"])
        )

        if monthly_sales.empty:
            st.caption("No monthly trend points for the selected period.")
        else:
            fig_line = px.line(
                monthly_sales,
                x="date",
                y="sales_amount",
                labels={"date": "Date", "sales_amount": "Total Sales (₱)"},
                markers=True,
                color_discrete_sequence=[ORANGE],
                title="Sales Trend Over Time"
            )
            fig_line.update_traces(connectgaps=False)
            _center_title(fig_line, 16)
            st.plotly_chart(fig_line, use_container_width=True)

    with chart_box_2:
        _icon("Performance Previews", "chart")
        viz_col1, viz_col2 = st.columns(2)

        # ---- Sales by Courier
        with viz_col1:
            if "courier_name" in filtered_df_rider.columns and "sales_amount" in filtered_df_rider.columns:
                # This aggregation is also faster
                courier_sales = (
                    filtered_df_rider.groupby("courier_name", dropna=False)["sales_amount"]
                    .sum()
                    .reset_index()
                    .sort_values("sales_amount", ascending=False)
                )
                if not courier_sales.empty:
                    chart_courier = create_bar_chart(courier_sales, "courier_name", "sales_amount", "Sales by Courier")
                    if chart_courier:
                        chart_courier.update_layout(coloraxis_showscale=False)
                        _center_title(chart_courier, 16)
                        st.plotly_chart(chart_courier, use_container_width=True)
                else:
                    st.info("No courier data for the selected period.")
            else:
                st.info("Courier fields not available.")

        # ---- Top 5 Products by Sales
        with viz_col2:
            # This logic now uses the pre-aggregated product data
            if not filtered_df_product.empty:
                value_col = "total_sales"
                
                if value_col and "product_name" in filtered_df_product.columns:
                    # This aggregation is also faster
                    top_products = (
                        filtered_df_product.groupby("product_name", dropna=False)[value_col]
                        .sum()
                        .nlargest(5)
                        .reset_index()
                    )
                    if not top_products.empty:
                        chart_product = create_bar_chart(top_products, "product_name", value_col, "Top 5 Products by Sales")
                        if chart_product:
                            chart_product.update_layout(coloraxis_showscale=False)
                            _center_title(chart_product, 16)
                            st.plotly_chart(chart_product, use_container_width=True)
                    else:
                        st.info("No product data for the selected period.")
                else:
                    st.info("Product fields not available.")
            else:
                st.info("No product data for the selected period.")