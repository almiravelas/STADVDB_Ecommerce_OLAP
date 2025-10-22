"""
Drill-down View - Disaggregation to lower levels of granularity
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from queries.drilldown_queries import (
    drilldown_year_to_month,
    drilldown_category_to_product,
    drilldown_month_to_day,
    drilldown_courier_to_vehicle
)
from queries.helper_queries import (
    get_available_years,
    get_available_categories,
    get_available_couriers
)


def show_drilldown_view(engine):
    """Display drill-down operations view"""
    st.markdown("""
    <style>
    .drilldown-header {
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background-color: #F1F8F4;
    }
    .drilldown-header h2 {
        color: #4CAF50;
        margin: 0;
    }
    .drilldown-header p {
        color: #333;
        margin-top: 0.5rem;
    }
    @media (prefers-color-scheme: dark) {
        .drilldown-header {
            background-color: #1a2d1f;
            border-color: #66BB6A;
        }
        .drilldown-header h2 {
            color: #66BB6A;
        }
        .drilldown-header p {
            color: #e0e0e0;
        }
    }
    </style>
    <div class='drilldown-header'>
        <h2>▤ Drill-down Operations</h2>
        <p>
            <strong>Drill-down</strong> navigates from higher to lower levels of detail, allowing you to explore data at finer granularity.
            For example: Year → Month → Day, or Category → Product.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Select drill-down dimension
    drilldown_option = st.selectbox(
        "Select Drill-down Path:",
        ["Time: Year → Month", "Time: Month → Day", "Product: Category → Product", "Rider: Courier → Vehicle Type"],
        key="drilldown_dimension"
    )
    
    st.divider()
    
    if drilldown_option == "Time: Year → Month":
        show_year_to_month_drilldown(engine)
    elif drilldown_option == "Time: Month → Day":
        show_month_to_day_drilldown(engine)
    elif drilldown_option == "Product: Category → Product":
        show_category_to_product_drilldown(engine)
    elif drilldown_option == "Rider: Courier → Vehicle Type":
        show_courier_to_vehicle_drilldown(engine)


def show_year_to_month_drilldown(engine):
    """Drill down from year to month"""
    st.subheader("📅 Drill Down: Year → Month")
    st.caption("Explore monthly details for a specific year")
    
    # Get available years
    years = get_available_years(engine)
    if not years:
        st.warning("No years available.")
        return
    
    selected_year = st.selectbox("Select Year to Drill Down:", years, key="dd_year")
    
    df, duration = drilldown_year_to_month(engine, selected_year)
    
    if df.empty:
        st.warning(f"No data available for year {selected_year}.")
        return
    
    st.info(f"Query executed in {duration:.4f} seconds")
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Year", selected_year)
    with col2:
        st.metric("Total Sales", f"₱{df['total_sales'].sum():,.2f}")
    with col3:
        st.metric("Total Orders", f"{df['total_orders'].sum():,}")
    with col4:
        st.metric("Avg Monthly Sales", f"₱{df['total_sales'].mean():,.2f}")
    
    # Data table
    st.subheader(f"Monthly Breakdown for {selected_year}")
    display_df = df.copy()
    display_df = display_df[['month', 'month_name', 'total_sales', 'total_orders', 'total_quantity', 'avg_order_value']]
    display_df['total_sales'] = display_df['total_sales'].apply(lambda x: f"₱{x:,.2f}")
    display_df['avg_order_value'] = display_df['avg_order_value'].apply(lambda x: f"₱{x:,.2f}")
    display_df['total_orders'] = display_df['total_orders'].apply(lambda x: f"{x:,}")
    display_df['total_quantity'] = display_df['total_quantity'].apply(lambda x: f"{x:,}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Monthly Sales Trend")
        fig = px.line(
            df,
            x='month_name',
            y='total_sales',
            markers=True,
            labels={'month_name': 'Month', 'total_sales': 'Total Sales (₱)'},
            text='total_sales'
        )
        fig.update_traces(texttemplate='₱%{text:,.0f}', textposition='top center', line_color='#FF6B35')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Monthly Order Volume")
        fig = px.bar(
            df,
            x='month_name',
            y='total_orders',
            labels={'month_name': 'Month', 'total_orders': 'Total Orders'},
            color='total_orders',
            color_continuous_scale='oranges'
        )
        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)


def show_month_to_day_drilldown(engine):
    """Drill down from month to day"""
    st.subheader("📅 Drill Down: Month → Day")
    st.caption("Explore daily details for a specific month")
    
    # Get available years
    years = get_available_years(engine)
    if not years:
        st.warning("No years available.")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("Select Year:", years, key="dd_month_year")
    with col2:
        selected_month = st.selectbox(
            "Select Month:",
            list(range(1, 13)),
            format_func=lambda x: pd.to_datetime(f"2000-{x:02d}-01").strftime('%B'),
            key="dd_month"
        )
    
    df, duration = drilldown_month_to_day(engine, selected_year, selected_month)
    
    if df.empty:
        month_name = pd.to_datetime(f"2000-{selected_month:02d}-01").strftime('%B')
        st.warning(f"No data available for {month_name} {selected_year}.")
        return
    
    st.info(f"Query executed in {duration:.4f} seconds")
    
    month_name = pd.to_datetime(f"2000-{selected_month:02d}-01").strftime('%B')
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Period", f"{month_name} {selected_year}")
    with col2:
        st.metric("Total Sales", f"₱{df['total_sales'].sum():,.2f}")
    with col3:
        st.metric("Total Orders", f"{df['total_orders'].sum():,}")
    with col4:
        st.metric("Avg Daily Sales", f"₱{df['total_sales'].mean():,.2f}")
    
    # Data table
    st.subheader(f"Daily Breakdown for {month_name} {selected_year}")
    display_df = df.copy()
    display_df['full_date'] = pd.to_datetime(display_df['full_date']).dt.strftime('%Y-%m-%d')
    display_df['is_weekend'] = display_df['is_weekend'].apply(lambda x: '✓' if x else '')
    display_df = display_df[['full_date', 'day_name', 'is_weekend', 'total_sales', 'total_orders', 'total_quantity']]
    display_df['total_sales'] = display_df['total_sales'].apply(lambda x: f"₱{x:,.2f}")
    display_df['total_orders'] = display_df['total_orders'].apply(lambda x: f"{x:,}")
    display_df['total_quantity'] = display_df['total_quantity'].apply(lambda x: f"{x:,}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Daily Sales Pattern")
        fig = px.bar(
            df,
            x='full_date',
            y='total_sales',
            color='is_weekend',
            labels={'full_date': 'Date', 'total_sales': 'Total Sales (₱)', 'is_weekend': 'Weekend'},
            color_discrete_map={True: '#FF6B35', False: '#FFA500'}
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Sales by Day of Week")
        day_sales = df.groupby('day_name')['total_sales'].sum().reset_index()
        # Order by weekday
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_sales['day_name'] = pd.Categorical(day_sales['day_name'], categories=day_order, ordered=True)
        day_sales = day_sales.sort_values('day_name')
        
        fig = px.bar(
            day_sales,
            x='day_name',
            y='total_sales',
            labels={'day_name': 'Day', 'total_sales': 'Total Sales (₱)'},
            color='total_sales',
            color_continuous_scale='oranges'
        )
        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)


def show_category_to_product_drilldown(engine):
    """Drill down from category to product"""
    st.subheader("🛍️ Drill Down: Category → Product")
    st.caption("Explore individual products within a category")
    
    # Get available categories
    categories = get_available_categories(engine)
    if not categories:
        st.warning("No categories available.")
        return
    
    selected_category = st.selectbox("Select Category to Drill Down:", categories, key="dd_category")
    
    df, duration = drilldown_category_to_product(engine, selected_category)
    
    if df.empty:
        st.warning(f"No products found in category: {selected_category}.")
        return
    
    st.info(f"Query executed in {duration:.4f} seconds")
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Category", selected_category)
    with col2:
        st.metric("Total Products", len(df))
    with col3:
        st.metric("Total Sales", f"₱{df['total_sales'].sum():,.2f}")
    with col4:
        st.metric("Total Orders", f"{df['total_orders'].sum():,}")
    
    # Data table
    st.subheader(f"Products in {selected_category}")
    display_df = df.copy()
    display_df = display_df[['product_name', 'price', 'total_sales', 'total_orders', 'total_quantity', 'avg_order_value']]
    display_df['price'] = display_df['price'].apply(lambda x: f"₱{x:,.2f}")
    display_df['total_sales'] = display_df['total_sales'].apply(lambda x: f"₱{x:,.2f}")
    display_df['avg_order_value'] = display_df['avg_order_value'].apply(lambda x: f"₱{x:,.2f}")
    display_df['total_orders'] = display_df['total_orders'].apply(lambda x: f"{x:,}")
    display_df['total_quantity'] = display_df['total_quantity'].apply(lambda x: f"{x:,}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 10 Products by Sales")
        top_products = df.nlargest(10, 'total_sales')
        fig = px.bar(
            top_products,
            y='product_name',
            x='total_sales',
            orientation='h',
            labels={'product_name': 'Product', 'total_sales': 'Total Sales (₱)'},
            color='total_sales',
            color_continuous_scale='oranges'
        )
        fig.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Sales vs Quantity Sold")
        fig = px.scatter(
            df,
            x='total_quantity',
            y='total_sales',
            size='total_orders',
            hover_data=['product_name'],
            labels={'total_quantity': 'Total Quantity', 'total_sales': 'Total Sales (₱)'},
            color='total_sales',
            color_continuous_scale='oranges'
        )
        st.plotly_chart(fig, use_container_width=True)


def show_courier_to_vehicle_drilldown(engine):
    """Drill down from courier to vehicle type"""
    st.subheader("🚚 Courier → Vehicle Type Drill-down")
    st.caption("Select a courier to see breakdown by vehicle type")
    
    # Get available couriers
    couriers = get_available_couriers(engine)
    if not couriers:
        st.warning("No courier data available.")
        return
    
    # Select courier
    selected_courier = st.selectbox(
        "Select Courier:",
        couriers,
        key="drilldown_courier"
    )
    
    if not selected_courier:
        return
    
    st.divider()
    
    # Execute drill-down query
    df, duration = drilldown_courier_to_vehicle(engine, selected_courier)
    
    if df.empty:
        st.warning(f"No vehicle data available for {selected_courier}.")
        return
    
    st.info(f"Query executed in {duration:.4f} seconds")
    st.success(f"Showing vehicle breakdown for: **{selected_courier}**")
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Vehicle Types", len(df))
    with col2:
        st.metric("Total Sales", f"₱{df['total_sales'].sum():,.2f}")
    with col3:
        st.metric("Total Orders", f"{df['total_orders'].sum():,}")
    with col4:
        st.metric("Total Riders", f"{df['rider_count'].sum():,}")
    
    # Data table
    st.subheader("Vehicle Type Breakdown")
    display_df = df.copy()
    display_df['total_sales'] = display_df['total_sales'].apply(lambda x: f"₱{x:,.2f}")
    display_df['avg_order_value'] = display_df['avg_order_value'].apply(lambda x: f"₱{x:,.2f}")
    display_df['total_orders'] = display_df['total_orders'].apply(lambda x: f"{x:,}")
    display_df['total_quantity'] = display_df['total_quantity'].apply(lambda x: f"{x:,}")
    display_df['rider_count'] = display_df['rider_count'].apply(lambda x: f"{x:,}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sales by Vehicle Type")
        fig = px.bar(
            df,
            x='vehicleType',
            y='total_sales',
            text='total_sales',
            labels={'vehicleType': 'Vehicle Type', 'total_sales': 'Total Sales (₱)'},
            color='total_sales',
            color_continuous_scale='greens'
        )
        fig.update_traces(texttemplate='₱%{text:,.0f}', textposition='outside')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Orders by Vehicle Type")
        fig = px.pie(
            df,
            values='total_orders',
            names='vehicleType',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Greens_r
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
