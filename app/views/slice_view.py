"""
Slice View - Selecting a single dimension value
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from queries.slice_queries import (
    slice_by_year,
    slice_by_category,
    slice_by_city,
    slice_by_courier
)
from queries.helper_queries import (
    get_available_years,
    get_available_categories,
    get_available_cities,
    get_available_couriers
)


def show_slice_view(engine):
    """Display slice operations view"""
    st.markdown("""
    <style>
    .slice-header {
        border: 2px solid #2196F3;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background-color: #E3F2FD;
    }
    .slice-header h2 {
        color: #2196F3;
        margin: 0;
    }
    .slice-header p {
        color: #333;
        margin-top: 0.5rem;
    }
    @media (prefers-color-scheme: dark) {
        .slice-header {
            background-color: #0d1f2d;
            border-color: #42A5F5;
        }
        .slice-header h2 {
            color: #42A5F5;
        }
        .slice-header p {
            color: #e0e0e0;
        }
    }
    </style>
    <div class='slice-header'>
        <h2>▥ Slice Operations</h2>
        <p>
            <strong>Slice</strong> selects a single value from one dimension, creating a sub-cube by fixing one dimension.
            For example: View all data for Year=2024, or Category='Electronics', or City='Manila'.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Select slice dimension
    slice_option = st.selectbox(
        "Select Dimension to Slice:",
        ["Time: By Year", "Product: By Category", "Location: By City", "Rider: By Courier"],
        key="slice_dimension"
    )
    
    st.divider()
    
    if slice_option == "Time: By Year":
        show_year_slice(engine)
    elif slice_option == "Product: By Category":
        show_category_slice(engine)
    elif slice_option == "Location: By City":
        show_city_slice(engine)
    elif slice_option == "Rider: By Courier":
        show_courier_slice(engine)


def show_year_slice(engine):
    """Slice by specific year"""
    st.subheader("📅 Slice by Year")
    st.caption("View all dimensions for a specific year")
    
    # Get available years
    all_years = get_available_years(engine)
    # Filter for 2024 and 2025
    years = [year for year in all_years if year in [2024, 2025]]
    
    if not years:
        st.warning("No data available for 2024 or 2025.")
        return
    
    selected_year = st.selectbox("Select Year:", years, key="slice_year")
    
    df, duration, query, params = slice_by_year(engine, selected_year)
    
    if df.empty:
        st.warning(f"No data available for year {selected_year}.")
        return
    
    st.info(f"Query executed in {duration:.4f} seconds | Rows returned: {len(df):,}")
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Year", selected_year)
    with col2:
        st.metric("Total Sales", f"₱{df['total_sales'].sum():,.2f}")
    with col3:
        st.metric("Total Orders", f"{df['total_orders'].sum():,}")
    with col4:
        st.metric("Total Quantity", f"{df['total_quantity'].sum():,}")
    
    # Summary by category
    st.subheader(f"Sales by Category in {selected_year}")
    category_summary = df.groupby('category').agg({
        'total_sales': 'sum',
        'total_orders': 'sum',
        'total_quantity': 'sum'
    }).reset_index().sort_values('total_sales', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        display_cat = category_summary.copy()
        display_cat['total_sales'] = display_cat['total_sales'].apply(lambda x: f"₱{x:,.2f}")
        display_cat['total_orders'] = display_cat['total_orders'].apply(lambda x: f"{x:,}")
        display_cat['total_quantity'] = display_cat['total_quantity'].apply(lambda x: f"{x:,}")
        st.dataframe(display_cat, use_container_width=True, hide_index=True)
    
    with col2:
        fig = px.pie(
            category_summary,
            values='total_sales',
            names='category',
            title=f'Sales Distribution by Category ({selected_year})',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Oranges_r
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Summary by month
    st.subheader(f"Sales by Month in {selected_year}")
    month_summary = df.groupby('month_name').agg({
        'total_sales': 'sum',
        'total_orders': 'sum'
    }).reset_index()
    
    # Order months properly
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    month_summary['month_name'] = pd.Categorical(month_summary['month_name'], categories=month_order, ordered=True)
    month_summary = month_summary.sort_values('month_name')
    
    fig = px.bar(
        month_summary,
        x='month_name',
        y='total_sales',
        labels={'month_name': 'Month', 'total_sales': 'Total Sales (₱)'},
        color='total_sales',
        color_continuous_scale='oranges'
    )
    fig.update_layout(showlegend=False, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Top cities
    st.subheader(f"Top User Cities in {selected_year}")
    city_summary = df.groupby('city').agg({
        'total_sales': 'sum',
        'total_orders': 'sum'
    }).reset_index().sort_values('total_sales', ascending=False).head(10)
    
    col1, col2 = st.columns(2)
    
    with col1:
        display_city = city_summary.copy()
        display_city['total_sales'] = display_city['total_sales'].apply(lambda x: f"₱{x:,.2f}")
        display_city['total_orders'] = display_city['total_orders'].apply(lambda x: f"{x:,}")
        st.dataframe(display_city, use_container_width=True, hide_index=True)
    
    with col2:
        fig = px.bar(
            city_summary,
            y='city',
            x='total_sales',
            orientation='h',
            labels={'city': 'City', 'total_sales': 'Total Sales (₱)'},
            color='total_sales',
            color_continuous_scale='oranges'
        )
        fig.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed data
    with st.expander("View Detailed Slice Data (First 100 rows)"):
        display_df = df.head(100).copy()
        display_df['total_sales'] = display_df['total_sales'].apply(lambda x: f"₱{x:,.2f}")
        display_df['total_orders'] = display_df['total_orders'].apply(lambda x: f"{x:,}")
        display_df['total_quantity'] = display_df['total_quantity'].apply(lambda x: f"{x:,}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)


def show_category_slice(engine):
    """Slice by specific category"""
    st.subheader("🛍️ Slice by Product Category")
    st.caption("View all dimensions for a specific product category")
    
    # Get available categories
    categories = get_available_categories(engine)
    if not categories:
        st.warning("No categories available.")
        return
    
    selected_category = st.selectbox("Select Category:", categories, key="slice_category")
    
    df, duration, query, params = slice_by_category(engine, selected_category)
    
    if df.empty:
        st.warning(f"No data available for category: {selected_category}.")
        return
    
    st.info(f"Query executed in {duration:.4f} seconds | Rows returned: {len(df):,}")
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Category", selected_category)
    with col2:
        st.metric("Total Sales", f"₱{df['total_sales'].sum():,.2f}")
    with col3:
        st.metric("Total Orders", f"{df['total_orders'].sum():,}")
    with col4:
        st.metric("Unique Products", df['product_name'].nunique())
    
    # Top products
    st.subheader(f"Top Products in {selected_category}")
    product_summary = df.groupby('product_name').agg({
        'total_sales': 'sum',
        'total_orders': 'sum',
        'total_quantity': 'sum'
    }).reset_index().sort_values('total_sales', ascending=False).head(10)
    
    col1, col2 = st.columns(2)
    
    with col1:
        display_prod = product_summary.copy()
        display_prod['total_sales'] = display_prod['total_sales'].apply(lambda x: f"₱{x:,.2f}")
        display_prod['total_orders'] = display_prod['total_orders'].apply(lambda x: f"{x:,}")
        display_prod['total_quantity'] = display_prod['total_quantity'].apply(lambda x: f"{x:,}")
        st.dataframe(display_prod, use_container_width=True, hide_index=True)
    
    with col2:
        fig = px.bar(
            product_summary,
            y='product_name',
            x='total_sales',
            orientation='h',
            labels={'product_name': 'Product', 'total_sales': 'Total Sales (₱)'},
            color='total_sales',
            color_continuous_scale='oranges'
        )
        fig.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Sales by year
    st.subheader(f"Yearly Trend for {selected_category}")
    year_summary = df.groupby('year').agg({
        'total_sales': 'sum',
        'total_orders': 'sum'
    }).reset_index().sort_values('year')
    
    # Filter for 2024, 2025
    year_summary = year_summary[year_summary['year'].isin([2024, 2025])]
    
    fig = px.line(
        year_summary,
        x='year',
        y='total_sales',
        markers=True,
        labels={'year': 'Year', 'total_sales': 'Total Sales (₱)'},
        text='total_sales'
    )
    fig.update_layout(showlegend=False, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Top cities
    st.subheader(f"Top User Cities for {selected_category}")
    city_summary = df.groupby('city').agg({
        'total_sales': 'sum',
        'total_orders': 'sum'
    }).reset_index().sort_values('total_sales', ascending=False).head(10)
    
    fig = px.bar(
        city_summary,
        x='city',
        y='total_sales',
        labels={'city': 'City', 'total_sales': 'Total Sales (₱)'},
        color='total_sales',
        color_continuous_scale='oranges'
    )
    fig.update_layout(showlegend=False, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed data
    with st.expander("View Detailed Slice Data (First 100 rows)"):
        display_df = df.head(100).copy()
        display_df['total_sales'] = display_df['total_sales'].apply(lambda x: f"₱{x:,.2f}")
        display_df['total_orders'] = display_df['total_orders'].apply(lambda x: f"{x:,}")
        display_df['total_quantity'] = display_df['total_quantity'].apply(lambda x: f"{x:,}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)


def show_city_slice(engine):
    """Slice by specific city"""
    st.subheader("📍 Slice by City")
    st.caption("View all dimensions for a specific user city")
    
    # Get available cities
    cities = get_available_cities(engine)
    if not cities:
        st.warning("No cities available.")
        return
    
    selected_city = st.selectbox("Select City:", cities, key="slice_city")
    
    df, duration, query, params = slice_by_city(engine, selected_city)
    
    if df.empty:
        st.warning(f"No data available for city: {selected_city}.")
        return
    
    st.info(f"Query executed in {duration:.4f} seconds | Rows returned: {len(df):,}")
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("City", selected_city)
    with col2:
        st.metric("Total Sales", f"₱{df['total_sales'].sum():,.2f}")
    with col3:
        st.metric("Total Orders", f"{df['total_orders'].sum():,}")
    with col4:
        st.metric("Total Quantity", f"{df['total_quantity'].sum():,}")
    
    # Sales by category
    st.subheader(f"Sales by Category in {selected_city}")
    category_summary = df.groupby('category').agg({
        'total_sales': 'sum',
        'total_orders': 'sum',
        'total_quantity': 'sum'
    }).reset_index().sort_values('total_sales', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        display_cat = category_summary.copy()
        display_cat['total_sales'] = display_cat['total_sales'].apply(lambda x: f"₱{x:,.2f}")
        display_cat['total_orders'] = display_cat['total_orders'].apply(lambda x: f"{x:,}")
        display_cat['total_quantity'] = display_cat['total_quantity'].apply(lambda x: f"{x:,}")
        st.dataframe(display_cat, use_container_width=True, hide_index=True)
    
    with col2:
        fig = px.pie(
            category_summary,
            values='total_sales',
            names='category',
            title=f'Category Distribution in {selected_city}',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Oranges_r
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top products
    st.subheader(f"Top Products in {selected_city}")
    product_summary = df.groupby('product_name').agg({
        'total_sales': 'sum',
        'total_orders': 'sum'
    }).reset_index().sort_values('total_sales', ascending=False).head(10)
    
    fig = px.bar(
        product_summary,
        y='product_name',
        x='total_sales',
        orientation='h',
        labels={'product_name': 'Product', 'total_sales': 'Total Sales (₱)'},
        color='total_sales',
        color_continuous_scale='oranges'
    )
    fig.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Yearly trend
    st.subheader(f"Yearly Sales Trend in {selected_city}")
    year_summary = df.groupby('year').agg({
        'total_sales': 'sum',
        'total_orders': 'sum'
    }).reset_index().sort_values('year')
    
    # Filter for 2024, 2025
    year_summary = year_summary[year_summary['year'].isin([2024, 2025])]
    
    fig = px.line(
        year_summary,
        x='year',
        y='total_sales',
        markers=True,
        labels={'year': 'Year', 'total_sales': 'Total Sales (₱)'},
        text='total_sales'
    )
    fig.update_traces(texttemplate='₱%{text:,.0f}', textposition='top center', line_color='#FF6B35')
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed data
    with st.expander("View Detailed Slice Data (First 100 rows)"):
        display_df = df.head(100).copy()
        display_df['total_sales'] = display_df['total_sales'].apply(lambda x: f"₱{x:,.2f}")
        display_df['total_orders'] = display_df['total_orders'].apply(lambda x: f"{x:,}")
        display_df['total_quantity'] = display_df['total_quantity'].apply(lambda x: f"{x:,}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)


def show_courier_slice(engine):
    st.subheader("🚚 Slice by Courier")
    st.caption("Fix the courier dimension to view data for a specific delivery service")
    
    # Get available couriers
    couriers = get_available_couriers(engine)
    if not couriers:
        st.warning("No courier data available.")
        return
    
    # Select courier to slice
    selected_courier = st.selectbox(
        "Select Courier:",
        couriers,
        key="slice_courier"
    )
    
    if not selected_courier:
        return
    
    st.divider()
    
    # Execute slice query
    df, duration, query, params = slice_by_courier(engine, selected_courier)
    
    if df.empty:
        st.warning(f"No data available for courier: {selected_courier}")
        return
    
    st.info(f"Query executed in {duration:.4f} seconds")
    st.success(f"Showing all data for courier: **{selected_courier}**")
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Sales", f"₱{df['total_sales'].sum():,.2f}")
    with col2:
        st.metric("Total Orders", f"₱{df['total_orders'].sum():,}")
    with col3:
        st.metric("Total Quantity", f"₱{df['total_quantity'].sum():,}")
    with col4:
        st.metric("Avg Order Value", f"₱{df['avg_order_value'].mean():,.2f}")
    
    # Multi-dimensional analysis
    st.subheader("Multi-Dimensional Analysis")
    
    # By vehicle type
    st.markdown("**By Vehicle Type**")
    vehicle_summary = df.groupby('vehicleType').agg({
        'total_sales': 'sum',
        'total_orders': 'sum',
        'total_quantity': 'sum'
    }).reset_index().sort_values('total_sales', ascending=False)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            vehicle_summary,
            x='vehicleType',
            y='total_sales',
            text='total_sales',
            labels={'vehicleType': 'Vehicle Type', 'total_sales': 'Total Sales (₱)'},
            color='total_sales',
            color_continuous_scale='blues'
        )
        fig.update_traces(texttemplate='₱%{text:,.0f}', textposition='outside')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(
            vehicle_summary,
            values='total_sales',
            names='vehicleType',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    # By category
    st.markdown("**By Category**")
    category_summary = df.groupby('category').agg({
        'total_sales': 'sum',
        'total_orders': 'sum'
    }).reset_index().sort_values('total_sales', ascending=False).head(10)
    
    fig = px.bar(
        category_summary,
        y='category',
        x='total_sales',
        orientation='h',
        text='total_sales',
        labels={'category': 'Category', 'total_sales': 'Total Sales (₱)'},
        color='total_sales',
        color_continuous_scale='blues'
    )
    fig.update_traces(texttemplate='₱%{text:,.0f}', textposition='outside')
    fig.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    # By year
    st.markdown("**By Year**")
    year_summary = df.groupby('year').agg({
        'total_sales': 'sum',
        'total_orders': 'sum'
    }).reset_index().sort_values('year')
    
    # Filter for 2024, 2025
    year_summary = year_summary[year_summary['year'].isin([2024, 2025])]
    
    fig = px.line(
        year_summary,
        x='year',
        y='total_sales',
        markers=True,
        labels={'year': 'Year', 'total_sales': 'Total Sales (₱)'},
        text='total_sales'
    )
    fig.update_traces(texttemplate='₱%{text:,.0f}', textposition='top center', line_color='#2196F3')
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed data
    with st.expander("View Detailed Slice Data (First 100 rows)"):
        display_df = df.head(100).copy()
        display_df['total_sales'] = display_df['total_sales'].apply(lambda x: f"₱{x:,.2f}")
        display_df['total_orders'] = display_df['total_orders'].apply(lambda x: f"{x:,}")
        display_df['total_quantity'] = display_df['total_quantity'].apply(lambda x: f"{x:,}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)