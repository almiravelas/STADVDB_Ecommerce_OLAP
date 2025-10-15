import streamlit as st
import pandas as pd
from utils.db_connection import get_warehouse_engine
from queries.rider_queries import get_sales_with_rider_details
from utils.charts import create_bar_chart
from views.icons import _inject_icon_css, _icon

@st.cache_data(ttl=600)
def load_rider_data(_engine):
    """Loads rider and sales data from the database, caching the result."""
    return get_sales_with_rider_details(_engine)

# --- Quarter helpers ---
QUARTER_LABELS = ["Q1", "Q2", "Q3", "Q4"]
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
    """Add a 'quarter' column derived from month if missing."""
    if "quarter" not in df.columns:
        if "month_name" in df.columns:
            df = df.copy()
            df["quarter"] = df["month_name"].map(MONTH_TO_Q)
        elif "month" in df.columns:
            def _q_from_m(m):
                if pd.isna(m): return None
                m = int(m)
                return (
                    QUARTER_LABELS[0] if m <= 3 else
                    QUARTER_LABELS[1] if m <= 6 else
                    QUARTER_LABELS[2] if m <= 9 else
                    QUARTER_LABELS[3]
                )
            df = df.copy()
            df["quarter"] = df["month"].apply(_q_from_m)
        else:
            df = df.copy()
            df["quarter"] = None
    return df

def show_rider_view(engine):
    """Renders the Rider Performance Analytics tab (quarter filters + title-sized headers)."""
    _inject_icon_css()

    _icon("Rider Performance Analytics", "truck", is_title=True)

    df = load_rider_data(engine)
    if df.empty:
        st.warning("No rider data available.")
        return

    df = _ensure_quarter(df)

    left_col, right_col = st.columns([1, 3])

    with left_col:
        with st.container(border=True):
            _icon("Filters", "filter")

            with st.expander("Date Filters", expanded=True):
                _icon("Date Filters", "calendar")
                years = sorted(df["year"].dropna().unique())
                year_sel = st.multiselect("Year", years, default=years)

                # Quarter filter replaces Month
                quarters_available = [q for q in QUARTER_LABELS if q in set(df["quarter"].dropna().unique())]
                if not quarters_available:
                    st.info("No quarter information found; showing all data.")
                    quarter_sel = QUARTER_LABELS
                else:
                    quarter_sel = st.multiselect("Quarter", quarters_available, default=quarters_available)

            with st.expander("Rider Attributes", expanded=True):
                _icon("Rider Attributes", "user")
                couriers = sorted(df["courier_name"].dropna().unique())
                courier_sel = st.multiselect("Courier", couriers, default=couriers)

                vehicles = sorted(df["vehicleType"].dropna().unique())
                vehicle_sel = st.multiselect("Vehicle Type", vehicles, default=vehicles)

                genders = sorted(df["gender"].dropna().unique())
                gender_sel = st.multiselect("Gender", genders, default=genders)

                if "age" in df.columns and not df["age"].dropna().empty:
                    min_age, max_age = int(df["age"].min()), int(df["age"].max())
                    age_range = st.slider("Age Range", min_value=min_age, max_value=max_age, value=(min_age, max_age))
                else:
                    age_range = (None, None)

        with st.container(border=True):
            _icon("Analysis Options", "filter")
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
                pivot_column_options = ["year", "quarter", "vehicleType", "gender"]
                pivot_column_selection = st.selectbox("Pivot On (Columns)", pivot_column_options)

    with right_col:
        group_col = {
            "Rider Name": "rider_name",
            "Courier Name": "courier_name",
            "Vehicle Type": "vehicleType",
            "Gender": "gender",
        }[group_by]

        mask = (
            df["year"].isin(year_sel) &
            (df["quarter"].isin(quarter_sel) if "quarter" in df.columns and quarter_sel else True) &
            df["courier_name"].isin(courier_sel) &
            df["vehicleType"].isin(vehicle_sel) &
            df["gender"].isin(gender_sel)
        )
        if age_range[0] is not None and age_range[1] is not None and "age" in df.columns:
            mask = mask & df["age"].between(age_range[0], age_range[1])

        filtered_df = df[mask]

        if display_mode == "Summary Chart":
            agg = filtered_df.groupby(group_col, dropna=False)["sales_amount"].sum().reset_index()
            agg = agg.sort_values(by="sales_amount", ascending=False)

            with st.container(border=True):
                _icon("Key Metrics", "metrics")
                if not agg.empty:
                    best, worst = agg.iloc[0], agg.iloc[-1]
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Total Riders", len(filtered_df["rider_name"].dropna().unique()))
                    c2.metric("Top Performer", best[group_col] if pd.notna(best[group_col]) else "—")
                    c3.metric("Lowest Performer", worst[group_col] if pd.notna(worst[group_col]) else "—")
                else:
                    st.info("No data available for the current filter selections.")

            with st.container(border=True):
                _icon(f"Top 10 Total Sales by {group_by}", "chart")
                chart = create_bar_chart(agg.head(10), group_col, "sales_amount", f"Sales by {group_by}")
                if chart:
                    st.plotly_chart(chart, use_container_width=True)

        else:
            with st.container(border=True):
                label = pivot_column_selection.title() if isinstance(pivot_column_selection, str) else "Columns"
                _icon(f"Sales Pivot: {group_by} vs. {label}", "table")
                if group_col == pivot_column_selection:
                    st.warning("Group By (Rows) and Pivot On (Columns) cannot be the same. Please select different options.")
                else:
                    try:
                        pivot_table = pd.pivot_table(
                            filtered_df,
                            values="sales_amount",
                            index=group_col,
                            columns=pivot_column_selection,
                            aggfunc="sum",
                            fill_value=0
                        )
                        st.dataframe(pivot_table.style.format("₱{:,.2f}"), use_container_width=True)
                    except Exception as e:
                        st.error(f"Could not create the pivot table: {e}")

        # Raw Data View
        with st.container(border=True):
            _icon("Data View", "data")
            if len(filtered_df) > 1000:
                st.info(f"Displaying the first 1,000 rows out of {len(filtered_df):,} total rows.")
                st.dataframe(filtered_df.head(1000), use_container_width=True, height=400)
            elif filtered_df.empty:
                st.info("No data to display for the current filter selection.")
            else:
                st.dataframe(filtered_df, use_container_width=True, height=400)
