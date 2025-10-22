"""
Dice View - Selecting multiple dimension values
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from queries.olap_queries import (
    dice_multi_dimension,
    get_available_years,
    get_available_categories,
    get_available_cities,
    get_available_couriers
)


def show_dice_view(engine):
    """Display dice operations view"""
    st.markdown("""
    <style>
    .dice-header {
        border: 2px solid #9C27B0;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background-color: #F3E5F5;
    }
    .dice-header h2 {
        color: #9C27B0;
        margin: 0;
    }
    .dice-header p {
        color: #333;
        margin-top: 0.5rem;
    }
    .dice-dimension {
        border: 1px solid;
        border-radius: 8px;
        padding: 1rem;
    }
    .dice-dimension h4 {
        margin: 0;
    }
    .dice-time {
        border-color: #FF9800;
        background-color: #FFF3E0;
    }
    .dice-time h4 {
        color: #E65100;
    }
    .dice-product {
        border-color: #4CAF50;
        background-color: #E8F5E9;
    }
    .dice-product h4 {
        color: #2E7D32;
    }
    .dice-location {
        border-color: #2196F3;
        background-color: #E3F2FD;
    }
    .dice-location h4 {
        color: #1565C0;
    }
    @media (prefers-color-scheme: dark) {
        .dice-header {
            background-color: #2d1a33;
            border-color: #BA68C8;
        }
        .dice-header h2 {
            color: #BA68C8;
        }
        .dice-header p {
            color: #e0e0e0;
        }
        .dice-time {
            border-color: #FFB74D;
            background-color: #2d2416;
        }
        .dice-time h4 {
            color: #FFB74D;
        }
        .dice-product {
            border-color: #66BB6A;
            background-color: #1a2d1f;
        }
        .dice-product h4 {
            color: #66BB6A;
        }
        .dice-location {
            border-color: #42A5F5;
            background-color: #0d1f2d;
        }
        .dice-location h4 {
            color: #42A5F5;
        }
    }
    </style>
    <div class='dice-header'>
        <h2>▦ Dice Operations</h2>
        <p>
            <strong>Dice</strong> selects multiple values from multiple dimensions, creating a sub-cube by specifying ranges or sets of values.
            For example: Years IN (2023, 2024) AND Categories IN ('Electronics', 'Fashion') AND Cities IN ('Manila', 'Cebu').
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Get available values for all dimensions
    years = get_available_years(engine)
    categories = get_available_categories(engine)
    cities = get_available_cities(engine)
    couriers = get_available_couriers(engine)
    
    if not years or not categories or not cities or not couriers:
        st.warning("Insufficient data available for dice operation.")
        return
    
    # Filter selection
    st.subheader("Select Dimension Values")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class='dice-dimension dice-time'>
            <h4>▨ Time</h4>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        selected_years = st.multiselect(
            "Select Years:",
            years,
            default=[years[-1]] if years else [],
            key="dice_years"
        )
    
    with col2:
        st.markdown("""
        <div class='dice-dimension dice-product'>
            <h4>▨ Product</h4>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        selected_categories = st.multiselect(
            "Select Categories:",
            categories,
            default=categories[:2] if len(categories) >= 2 else categories,
            key="dice_categories"
        )
    
    with col3:
        st.markdown("""
        <div class='dice-dimension dice-location'>
            <h4>▨ Location</h4>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        selected_cities = st.multiselect(
            "Select Cities:",
            cities,
            default=cities[:3] if len(cities) >= 3 else cities,
            key="dice_cities"
        )
    
    with col4:
        st.markdown("""
        <div class='dice-dimension dice-rider' style='border-color: #9C27B0; background-color: #F3E5F5;'>
            <h4 style='color: #6A1B9A;'>▨ Rider</h4>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        selected_couriers = st.multiselect(
            "Select Couriers:",
            couriers,
            default=couriers[:2] if len(couriers) >= 2 else couriers,
            key="dice_couriers"
        )
    
    st.divider()
    
    # Validate selections
    if not selected_years and not selected_categories and not selected_cities and not selected_couriers:
        st.info("Please select at least one value from any dimension to perform dice operation.")
        return
    
    # Show active filters
    st.subheader("🔍 Active Filters")
    filter_cols = st.columns(4)
    with filter_cols[0]:
        if selected_years:
            st.success(f"**Years:** {', '.join(map(str, selected_years))}")
        else:
            st.info("**Years:** All")
    with filter_cols[1]:
        if selected_categories:
            st.success(f"**Categories:** {', '.join(selected_categories)}")
        else:
            st.info("**Categories:** All")
    with filter_cols[2]:
        if selected_cities:
            st.success(f"**Cities:** {', '.join(selected_cities)}")
        else:
            st.info("**Cities:** All")
    with filter_cols[3]:
        if selected_couriers:
            st.success(f"**Couriers:** {', '.join(selected_couriers)}")
        else:
            st.info("**Couriers:** All")
    
    # Execute dice query
    df, duration = dice_multi_dimension(engine, selected_years, selected_categories, selected_cities, selected_couriers)
    
    if df.empty:
        st.warning("No data matches the selected criteria.")
        return
    
    st.info(f"Query executed in {duration:.4f} seconds | Rows returned: {len(df):,}")
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Sales", f"₱{df['total_sales'].sum():,.2f}")
    with col2:
        st.metric("Total Orders", f"{df['total_orders'].sum():,}")
    with col3:
        st.metric("Total Quantity", f"{df['total_quantity'].sum():,}")
    with col4:
        st.metric("Avg Order Value", f"₱{(df['total_sales'].sum() / df['total_orders'].sum()):,.2f}")
    
    st.divider()
    
    # Analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Summary Analysis",
        "📈 Trend Analysis",
        "🎯 Top Performers",
        "📋 Detailed Data"
    ])
    
    with tab1:
        show_summary_analysis(df)
    
    with tab2:
        show_trend_analysis(df, selected_years)
    
    with tab3:
        show_top_performers(df)
    
    with tab4:
        show_detailed_data(df)


def show_summary_analysis(df):
    """Show summary analysis of diced data"""
    st.subheader("Summary by Dimensions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # By Category
        st.markdown("**Sales by Category**")
        cat_summary = df.groupby('category').agg({
            'total_sales': 'sum',
            'total_orders': 'sum'
        }).reset_index().sort_values('total_sales', ascending=False)
        
        fig = px.pie(
            cat_summary,
            values='total_sales',
            names='category',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Oranges_r
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
        
        display_cat = cat_summary.copy()
        display_cat['total_sales'] = display_cat['total_sales'].apply(lambda x: f"₱{x:,.2f}")
        display_cat['total_orders'] = display_cat['total_orders'].apply(lambda x: f"{x:,}")
        st.dataframe(display_cat, use_container_width=True, hide_index=True)
    
    with col2:
        # By City
        st.markdown("**Sales by City**")
        city_summary = df.groupby('user_city').agg({
            'total_sales': 'sum',
            'total_orders': 'sum'
        }).reset_index().sort_values('total_sales', ascending=False).head(10)
        
        fig = px.bar(
            city_summary,
            y='user_city',
            x='total_sales',
            orientation='h',
            labels={'user_city': 'City', 'total_sales': 'Total Sales (₱)'},
            color='total_sales',
            color_continuous_scale='oranges'
        )
        fig.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
        display_city = city_summary.copy()
        display_city['total_sales'] = display_city['total_sales'].apply(lambda x: f"₱{x:,.2f}")
        display_city['total_orders'] = display_city['total_orders'].apply(lambda x: f"{x:,}")
        st.dataframe(display_city, use_container_width=True, hide_index=True)


def show_trend_analysis(df, selected_years):
    """Show trend analysis"""
    st.subheader("Temporal Trends")
    
    if not selected_years or len(selected_years) == 0:
        st.info("Select specific years to see detailed temporal trends.")
        return
    
    # Monthly trend
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    monthly_summary = df.groupby(['year', 'month_name']).agg({
        'total_sales': 'sum',
        'total_orders': 'sum'
    }).reset_index()
    
    monthly_summary['month_name'] = pd.Categorical(
        monthly_summary['month_name'], 
        categories=month_order, 
        ordered=True
    )
    monthly_summary = monthly_summary.sort_values(['year', 'month_name'])
    monthly_summary['year_month'] = monthly_summary['year'].astype(str) + '-' + monthly_summary['month_name'].astype(str)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Monthly Sales Trend**")
        fig = px.line(
            monthly_summary,
            x='year_month',
            y='total_sales',
            markers=True,
            labels={'year_month': 'Month', 'total_sales': 'Total Sales (₱)'},
            color='year',
            color_discrete_sequence=px.colors.sequential.Oranges_r
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Monthly Order Volume**")
        fig = px.bar(
            monthly_summary,
            x='year_month',
            y='total_orders',
            labels={'year_month': 'Month', 'total_orders': 'Total Orders'},
            color='year',
            color_discrete_sequence=px.colors.sequential.Oranges_r
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)


def show_top_performers(df):
    """Show top performers"""
    st.subheader("Top Performers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Top 10 Products by Sales**")
        product_summary = df.groupby('product_name').agg({
            'total_sales': 'sum',
            'total_orders': 'sum',
            'total_quantity': 'sum'
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
        
        display_prod = product_summary.copy()
        display_prod['total_sales'] = display_prod['total_sales'].apply(lambda x: f"₱{x:,.2f}")
        display_prod['total_orders'] = display_prod['total_orders'].apply(lambda x: f"{x:,}")
        display_prod['total_quantity'] = display_prod['total_quantity'].apply(lambda x: f"{x:,}")
        st.dataframe(display_prod, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("**Category Performance Comparison**")
        category_summary = df.groupby('category').agg({
            'total_sales': 'sum',
            'total_orders': 'sum',
            'total_quantity': 'sum'
        }).reset_index().sort_values('total_sales', ascending=False)
        
        fig = px.bar(
            category_summary,
            x='category',
            y=['total_sales', 'total_orders', 'total_quantity'],
            barmode='group',
            labels={'value': 'Count', 'variable': 'Metric', 'category': 'Category'},
            color_discrete_sequence=['#FF6B35', '#FFA500', '#FFD700']
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        display_cat = category_summary.copy()
        display_cat['total_sales'] = display_cat['total_sales'].apply(lambda x: f"₱{x:,.2f}")
        display_cat['total_orders'] = display_cat['total_orders'].apply(lambda x: f"{x:,}")
        display_cat['total_quantity'] = display_cat['total_quantity'].apply(lambda x: f"{x:,}")
        st.dataframe(display_cat, use_container_width=True, hide_index=True)


def show_detailed_data(df):
    """Show detailed data table"""
    st.subheader("Detailed Diced Data")
    
    # Add sorting options
    sort_by = st.selectbox(
        "Sort by:",
        ['total_sales', 'total_orders', 'total_quantity'],
        format_func=lambda x: x.replace('_', ' ').title(),
        key="dice_sort"
    )
    
    sort_order = st.radio("Order:", ['Descending', 'Ascending'], horizontal=True, key="dice_order")
    
    # Sort data
    sorted_df = df.sort_values(sort_by, ascending=(sort_order == 'Ascending'))
    
    # Display limit
    display_limit = st.slider("Number of rows to display:", 10, 500, 100, 10, key="dice_limit")
    
    # Format and display
    display_df = sorted_df.head(display_limit).copy()
    display_df['total_sales'] = display_df['total_sales'].apply(lambda x: f"₱{x:,.2f}")
    display_df['total_orders'] = display_df['total_orders'].apply(lambda x: f"{x:,}")
    display_df['total_quantity'] = display_df['total_quantity'].apply(lambda x: f"{x:,}")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Download option
    if st.button("📥 Download Complete Data as CSV"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="dice_operation_results.csv",
            mime="text/csv"
        )
