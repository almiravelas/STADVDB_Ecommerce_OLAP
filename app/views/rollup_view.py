"""
Roll-up View - Aggregation to higher levels of granularity
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from queries.olap_queries import (
    rollup_sales_by_year,
    rollup_sales_by_quarter,
    rollup_sales_by_category,
    rollup_sales_by_courier
)


def show_rollup_view(engine):
    """Display roll-up operations view"""
    st.markdown("""
    <style>
    .rollup-header {
        border: 2px solid #FF6B35;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background-color: #FFF5F0;
    }
    .rollup-header h2 {
        color: #FF6B35;
        margin: 0;
    }
    .rollup-header p {
        color: #333;
        margin-top: 0.5rem;
    }
    @media (prefers-color-scheme: dark) {
        .rollup-header {
            background-color: #2d1a14;
            border-color: #FF8C5A;
        }
        .rollup-header h2 {
            color: #FF8C5A;
        }
        .rollup-header p {
            color: #e0e0e0;
        }
    }
    </style>
    <div class='rollup-header'>
        <h2>▣ Roll-up Operations</h2>
        <p>
            <strong>Roll-up</strong> aggregates data by climbing up the concept hierarchy, moving from lower to higher levels of granularity.
            For example: Day → Month → Quarter → Year, or Product → Category.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Select roll-up dimension
    rollup_option = st.selectbox(
        "Select Roll-up Dimension:",
        ["Time: Year Level", "Time: Quarter Level", "Product: Category Level", "Rider: Courier Level"],
        key="rollup_dimension"
    )
    
    st.divider()
    
    if rollup_option == "Time: Year Level":
        show_year_rollup(engine)
    elif rollup_option == "Time: Quarter Level":
        show_quarter_rollup(engine)
    elif rollup_option == "Product: Category Level":
        show_category_rollup(engine)
    elif rollup_option == "Rider: Courier Level":
        show_courier_rollup(engine)


def show_year_rollup(engine):
    """Roll-up to year level"""
    st.markdown("""
    <div style='border-left: 4px solid #FF6B35; padding-left: 1rem; margin-bottom: 1rem;'>
        <h3 style='color: #FF6B35; margin: 0;'>▨ Sales Rolled Up by Year</h3>
        <p style='color: #666; margin: 0.3rem 0 0 0; font-size: 0.9rem;'>Highest level of time aggregation</p>
    </div>
    """, unsafe_allow_html=True)
    
    df, duration = rollup_sales_by_year(engine)
    
    if df.empty:
        st.warning("No data available for year roll-up.")
        return
    
    st.info(f"Query executed in {duration:.4f} seconds")
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Years", len(df))
    with col2:
        st.metric("Total Sales", f"₱{df['total_sales'].sum():,.2f}")
    with col3:
        st.metric("Total Orders", f"{df['total_orders'].sum():,}")
    with col4:
        st.metric("Total Quantity", f"{df['total_quantity'].sum():,}")
    
    # Data table
    st.subheader("Yearly Summary")
    display_df = df.copy()
    display_df['total_sales'] = display_df['total_sales'].apply(lambda x: f"₱{x:,.2f}")
    display_df['avg_order_value'] = display_df['avg_order_value'].apply(lambda x: f"₱{x:,.2f}")
    display_df['total_orders'] = display_df['total_orders'].apply(lambda x: f"{x:,}")
    display_df['total_quantity'] = display_df['total_quantity'].apply(lambda x: f"{x:,}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Total Sales by Year")
        fig = px.bar(
            df,
            x='year',
            y='total_sales',
            text='total_sales',
            labels={'year': 'Year', 'total_sales': 'Total Sales (₱)'},
            color='total_sales',
            color_continuous_scale='oranges'
        )
        fig.update_traces(texttemplate='₱%{text:,.0f}', textposition='outside')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Total Orders by Year")
        fig = px.line(
            df,
            x='year',
            y='total_orders',
            markers=True,
            labels={'year': 'Year', 'total_orders': 'Total Orders'},
            text='total_orders'
        )
        fig.update_traces(texttemplate='%{text:,}', textposition='top center', line_color='#FF6B35')
        st.plotly_chart(fig, use_container_width=True)


def show_quarter_rollup(engine):
    """Roll-up to quarter level"""
    st.markdown("""
    <div style='border-left: 4px solid #FF6B35; padding-left: 1rem; margin-bottom: 1rem;'>
        <h3 style='color: #FF6B35; margin: 0;'>▨ Sales Rolled Up by Quarter</h3>
        <p style='color: #666; margin: 0.3rem 0 0 0; font-size: 0.9rem;'>Quarterly aggregation across all years</p>
    </div>
    """, unsafe_allow_html=True)
    
    df, duration = rollup_sales_by_quarter(engine)
    
    if df.empty:
        st.warning("No data available for quarter roll-up.")
        return
    
    st.info(f"Query executed in {duration:.4f} seconds")
    
    # Add year-quarter label
    df['year_quarter'] = df['year'].astype(str) + '-Q' + df['quarter'].astype(str)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Quarters", len(df))
    with col2:
        st.metric("Total Sales", f"₱{df['total_sales'].sum():,.2f}")
    with col3:
        st.metric("Total Orders", f"{df['total_orders'].sum():,}")
    with col4:
        st.metric("Avg Quarter Sales", f"₱{df['total_sales'].mean():,.2f}")
    
    # Data table
    st.subheader("Quarterly Summary")
    display_df = df.copy()
    display_df = display_df[['year', 'quarter', 'year_quarter', 'total_sales', 'total_orders', 'total_quantity', 'avg_order_value']]
    display_df['total_sales'] = display_df['total_sales'].apply(lambda x: f"₱{x:,.2f}")
    display_df['avg_order_value'] = display_df['avg_order_value'].apply(lambda x: f"₱{x:,.2f}")
    display_df['total_orders'] = display_df['total_orders'].apply(lambda x: f"{x:,}")
    display_df['total_quantity'] = display_df['total_quantity'].apply(lambda x: f"{x:,}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Quarterly Sales Trend")
        fig = px.bar(
            df,
            x='year_quarter',
            y='total_sales',
            labels={'year_quarter': 'Quarter', 'total_sales': 'Total Sales (₱)'},
            color='total_sales',
            color_continuous_scale='oranges'
        )
        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Average Order Value by Quarter")
        fig = px.line(
            df,
            x='year_quarter',
            y='avg_order_value',
            markers=True,
            labels={'year_quarter': 'Quarter', 'avg_order_value': 'Avg Order Value (₱)'}
        )
        fig.update_traces(line_color='#FF6B35')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)


def show_category_rollup(engine):
    """Roll-up to product category level"""
    st.markdown("""
    <div style='border-left: 4px solid #FF6B35; padding-left: 1rem; margin-bottom: 1rem;'>
        <h3 style='color: #FF6B35; margin: 0;'>▨ Sales Rolled Up by Product Category</h3>
        <p style='color: #666; margin: 0.3rem 0 0 0; font-size: 0.9rem;'>Product aggregation at category level</p>
    </div>
    """, unsafe_allow_html=True)
    
    df, duration = rollup_sales_by_category(engine)
    
    if df.empty:
        st.warning("No data available for category roll-up.")
        return
    
    st.info(f"Query executed in {duration:.4f} seconds")
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Categories", len(df))
    with col2:
        st.metric("Total Sales", f"₱{df['total_sales'].sum():,.2f}")
    with col3:
        st.metric("Total Products", f"{df['product_count'].sum():,}")
    with col4:
        st.metric("Avg Category Sales", f"₱{df['total_sales'].mean():,.2f}")
    
    # Data table
    st.subheader("Category Summary")
    display_df = df.copy()
    display_df['total_sales'] = display_df['total_sales'].apply(lambda x: f"₱{x:,.2f}")
    display_df['avg_order_value'] = display_df['avg_order_value'].apply(lambda x: f"₱{x:,.2f}")
    display_df['total_orders'] = display_df['total_orders'].apply(lambda x: f"{x:,}")
    display_df['total_quantity'] = display_df['total_quantity'].apply(lambda x: f"{x:,}")
    display_df['product_count'] = display_df['product_count'].apply(lambda x: f"{x:,}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sales by Category")
        fig = px.bar(
            df,
            x='category',
            y='total_sales',
            text='total_sales',
            labels={'category': 'Category', 'total_sales': 'Total Sales (₱)'},
            color='total_sales',
            color_continuous_scale='oranges'
        )
        fig.update_traces(texttemplate='₱%{text:,.0f}', textposition='outside')
        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Sales Distribution by Category")
        fig = px.pie(
            df,
            values='total_sales',
            names='category',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Oranges_r
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)


def show_courier_rollup(engine):
    """Roll-up to courier level"""
    st.markdown("""
    <div style='border-left: 4px solid #FF6B35; padding-left: 1rem; margin-bottom: 1rem;'>
        <h3 style='color: #FF6B35; margin: 0;'>▨ Sales Rolled Up by Courier</h3>
        <p style='color: #666; margin: 0.3rem 0 0 0; font-size: 0.9rem;'>Delivery service aggregation at courier level</p>
    </div>
    """, unsafe_allow_html=True)
    
    df, duration = rollup_sales_by_courier(engine)
    
    if df.empty:
        st.warning("No data available for courier roll-up.")
        return
    
    st.info(f"Query executed in {duration:.4f} seconds")
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Couriers", len(df))
    with col2:
        st.metric("Total Sales", f"₱{df['total_sales'].sum():,.2f}")
    with col3:
        st.metric("Total Orders", f"{df['total_orders'].sum():,}")
    with col4:
        st.metric("Total Riders", f"{df['rider_count'].sum():,}")
    
    # Data table
    st.subheader("Courier Summary")
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
        st.subheader("Total Sales by Courier")
        fig = px.bar(
            df,
            x='courier_name',
            y='total_sales',
            text='total_sales',
            labels={'courier_name': 'Courier', 'total_sales': 'Total Sales (₱)'},
            color='total_sales',
            color_continuous_scale='oranges'
        )
        fig.update_traces(texttemplate='₱%{text:,.0f}', textposition='outside')
        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Market Share by Courier")
        fig = px.pie(
            df,
            values='total_sales',
            names='courier_name',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Oranges_r
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
