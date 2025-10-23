"""
Pivot View - Rotating data for different perspectives
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from queries.pivot_queries import (
    pivot_category_by_month,
    pivot_city_by_category,
    pivot_year_by_quarter
)


def show_pivot_view(engine):
    """Display pivot operations view"""
    st.markdown("""
    <style>
    .pivot-header {
        border: 2px solid #F57F17;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background-color: #FFFDE7;
    }
    .pivot-header h2 {
        color: #F57F17;
        margin: 0;
    }
    .pivot-header p {
        color: #333;
        margin-top: 0.5rem;
    }
    @media (prefers-color-scheme: dark) {
        .pivot-header {
            background-color: #2d2a14;
            border-color: #FDD835;
        }
        .pivot-header h2 {
            color: #FDD835;
        }
        .pivot-header p {
            color: #e0e0e0;
        }
    }
    </style>
    <div class='pivot-header'>
        <h2>▧ Pivot Operations</h2>
        <p>
            <strong>Pivot</strong> rotates the data axes to provide alternative presentations of the data.
            It allows you to view the same data from different perspectives by swapping rows and columns.
            For example: View Categories × Months or Cities × Categories matrix.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Select pivot type
    pivot_option = st.selectbox(
        "Select Pivot Perspective:",
        [
            "Categories × Months (Time Series)",
            "Cities × Categories (Geographic Distribution)",
            "Years × Quarters (Temporal Overview)"
        ],
        key="pivot_type"
    )
    
    st.divider()
    
    if pivot_option == "Categories × Months (Time Series)":
        show_category_month_pivot(engine)
    elif pivot_option == "Cities × Categories (Geographic Distribution)":
        show_city_category_pivot(engine)
    elif pivot_option == "Years × Quarters (Temporal Overview)":
        show_year_quarter_pivot(engine)


def show_category_month_pivot(engine):
    """Pivot: Categories as rows, months as columns"""
    st.subheader("🛍️ × 📅 Categories by Month Pivot")
    st.caption("Product categories across different months")
    
    df, duration = pivot_category_by_month(engine)
    
    if df.empty:
        st.warning("No data available for category-month pivot.")
        return
    
    st.info(f"Query executed in {duration:.4f} seconds")
    
    # Create year-month column for better grouping
    df['year_month'] = df['year'].astype(str) + '-' + df['month_name']
    
    # Select year for focused view
    all_available_years = sorted(df['year'].unique())
    # Filter for 2024 and 2025
    available_years = [year for year in all_available_years if year in [2024, 2025]]
    
    if not available_years:
        st.warning("No data available for 2024 or 2025.")
        return
        
    selected_year = st.selectbox("Select Year for Detailed View:", available_years, key="pivot_cat_year")
    
    df_year = df[df['year'] == selected_year].copy()
    
    # Create pivot table
    pivot_table = df_year.pivot_table(
        values='total_sales',
        index='category',
        columns='month_name',
        aggfunc='sum',
        fill_value=0
    )
    
    # Reorder columns by month
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    pivot_table = pivot_table.reindex(columns=[m for m in month_order if m in pivot_table.columns])
    
    # Calculate totals
    pivot_table['Total'] = pivot_table.sum(axis=1)
    pivot_table = pivot_table.sort_values('Total', ascending=False)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Year", selected_year)
    with col2:
        st.metric("Categories", len(pivot_table))
    with col3:
        st.metric("Total Sales", f"₱{pivot_table['Total'].sum():,.2f}")
    with col4:
        st.metric("Best Month", pivot_table.drop('Total', axis=1).sum().idxmax() if len(pivot_table) > 0 else "N/A")
    
    # Display pivot table
    st.subheader(f"Sales Pivot Table ({selected_year})")
    display_pivot = pivot_table.copy()
    display_pivot = display_pivot.applymap(lambda x: f"₱{x:,.0f}" if x != 0 else "—")
    st.dataframe(display_pivot, use_container_width=True)
    
    # Heatmap visualization
    st.subheader("Sales Heatmap")
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.drop('Total', axis=1).values,
        x=pivot_table.drop('Total', axis=1).columns,
        y=pivot_table.index,
        colorscale='Oranges',
        text=pivot_table.drop('Total', axis=1).values,
        texttemplate='₱%{text:,.0f}',
        textfont={"size": 10},
        colorbar=dict(title="Sales (₱)")
    ))
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Category",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Line chart for trends
    st.subheader("Category Sales Trends")
    
    # Prepare data for line chart
    line_data = df_year.groupby(['month', 'month_name', 'category'])['total_sales'].sum().reset_index()
    line_data = line_data.sort_values('month')
    
    fig = px.line(
        line_data,
        x='month_name',
        y='total_sales',
        color='category',
        markers=True,
        labels={'month_name': 'Month', 'total_sales': 'Total Sales (₱)', 'category': 'Category'},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(xaxis_tickangle=-45, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)
    
    # All years comparison
    st.subheader("Multi-Year Category Performance")
    # Filter original df for only 2024 and 2025 to show in comparison chart
    df_filtered_years = df[df['year'].isin([2024, 2025])]
    yearly_category = df_filtered_years.groupby(['year', 'category'])['total_sales'].sum().reset_index()
    
    fig = px.bar(
        yearly_category,
        x='category',
        y='total_sales',
        color='year',
        barmode='group',
        labels={'category': 'Category', 'total_sales': 'Total Sales (₱)', 'year': 'Year'},
        color_discrete_sequence=px.colors.sequential.Oranges_r
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)


def show_city_category_pivot(engine):
    """Pivot: Cities as rows, categories as columns"""
    st.subheader("📍 × 🛍️ Cities by Category Pivot")
    st.caption("Geographic distribution across product categories")
    
    df, duration = pivot_city_by_category(engine)
    
    if df.empty:
        st.warning("No data available for city-category pivot.")
        return
    
    st.info(f"Query executed in {duration:.4f} seconds")
    
    # Create pivot table for sales
    pivot_sales = df.pivot_table(
        values='total_sales',
        index='city',
        columns='category',
        aggfunc='sum',
        fill_value=0
    )
    
    # Calculate totals
    pivot_sales['Total'] = pivot_sales.sum(axis=1)
    pivot_sales = pivot_sales.sort_values('Total', ascending=False)
    
    # Top cities selection
    top_n = st.slider("Number of cities to display:", 5, 30, 15, key="pivot_city_top")
    pivot_sales_top = pivot_sales.head(top_n)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Cities", len(pivot_sales))
    with col2:
        st.metric("Categories", len(df['category'].unique()))
    with col3:
        st.metric("Total Sales", f"₱{pivot_sales['Total'].sum():,.2f}")
    with col4:
        best_city = pivot_sales.index[0] if len(pivot_sales) > 0 else "N/A"
        st.metric("Top City", best_city)
    
    # Display pivot table
    st.subheader(f"Sales Pivot Table (Top {top_n} Cities)")
    display_pivot = pivot_sales_top.copy()
    display_pivot = display_pivot.applymap(lambda x: f"₱{x:,.0f}" if x != 0 else "—")
    st.dataframe(display_pivot, use_container_width=True)
    
    # Heatmap visualization
    st.subheader("City-Category Sales Heatmap")
    fig = go.Figure(data=go.Heatmap(
        z=pivot_sales_top.drop('Total', axis=1).values,
        x=pivot_sales_top.drop('Total', axis=1).columns,
        y=pivot_sales_top.index,
        colorscale='Oranges',
        text=pivot_sales_top.drop('Total', axis=1).values,
        texttemplate='₱%{text:,.0f}',
        textfont={"size": 9},
        colorbar=dict(title="Sales (₱)")
    ))
    fig.update_layout(
        xaxis_title="Category",
        yaxis_title="City",
        height=max(400, top_n * 20)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Stacked bar chart
    st.subheader("Category Distribution by City")
    
    # Prepare data for stacked bar
    plot_data = pivot_sales_top.drop('Total', axis=1)
    
    fig = go.Figure()
    for category in plot_data.columns:
        fig.add_trace(go.Bar(
            name=category,
            y=plot_data.index,
            x=plot_data[category],
            orientation='h',
            text=plot_data[category],
            texttemplate='₱%{text:,.0f}',
            textposition='inside'
        ))
    
    fig.update_layout(
        barmode='stack',
        xaxis_title='Total Sales (₱)',
        yaxis_title='City',
        height=max(400, top_n * 25),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis={'categoryorder': 'total ascending'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Category breakdown
    st.subheader("Total Sales by Category (All Cities)")
    category_totals = df.groupby('category')['total_sales'].sum().reset_index().sort_values('total_sales', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        display_cat = category_totals.copy()
        display_cat['total_sales'] = display_cat['total_sales'].apply(lambda x: f"₱{x:,.2f}")
        st.dataframe(display_cat, use_container_width=True, hide_index=True)
    
    with col2:
        fig = px.pie(
            category_totals,
            values='total_sales',
            names='category',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Oranges_r
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)


def show_year_quarter_pivot(engine):
    """Pivot: Years as rows, quarters as columns"""
    st.subheader("📅 × 📊 Years by Quarter Pivot")
    st.caption("Quarterly performance across different years")
    
    df, duration = pivot_year_by_quarter(engine)
    
    if df.empty:
        st.warning("No data available for year-quarter pivot.")
        return
    
    st.info(f"Query executed in {duration:.4f} seconds")
    
    # Filter for 2024 and 2025
    df = df[df['year'].isin([2024, 2025])].copy()
    
    if df.empty:
        st.warning("No data available for 2024 or 2025.")
        return
    
    # Create pivot table for sales
    pivot_sales = df.pivot_table(
        values='total_sales',
        index='year',
        columns='quarter',
        aggfunc='sum',
        fill_value=0
    )
    
    # Ensure all quarters are present
    for q in [1, 2, 3, 4]:
        if q not in pivot_sales.columns:
            pivot_sales[q] = 0
    pivot_sales = pivot_sales[[1, 2, 3, 4]]
    pivot_sales.columns = [f'Q{i}' for i in pivot_sales.columns]
    
    # Calculate totals
    pivot_sales['Total'] = pivot_sales.sum(axis=1)
    
    # Create pivot table for orders
    pivot_orders = df.pivot_table(
        values='total_orders',
        index='year',
        columns='quarter',
        aggfunc='sum',
        fill_value=0
    )
    for q in [1, 2, 3, 4]:
        if q not in pivot_orders.columns:
            pivot_orders[q] = 0
    pivot_orders = pivot_orders[[1, 2, 3, 4]]
    pivot_orders.columns = [f'Q{i}' for i in pivot_orders.columns]
    pivot_orders['Total'] = pivot_orders.sum(axis=1)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Years", len(pivot_sales))
    with col2:
        st.metric("Total Sales", f"₱{pivot_sales['Total'].sum():,.2f}")
    with col3:
        st.metric("Total Orders", f"{pivot_orders['Total'].sum():,}")
    with col4:
        best_quarter = pivot_sales.drop('Total', axis=1).sum().idxmax() if len(pivot_sales) > 0 else "N/A"
        st.metric("Best Quarter", best_quarter)
    
    # Display pivot tables
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sales by Quarter")
        display_sales = pivot_sales.copy()
        display_sales = display_sales.applymap(lambda x: f"₱{x:,.0f}")
        st.dataframe(display_sales, use_container_width=True)
    
    with col2:
        st.subheader("Orders by Quarter")
        display_orders = pivot_orders.copy()
        display_orders = display_orders.applymap(lambda x: f"{x:,}")
        st.dataframe(display_orders, use_container_width=True)
    
    # Heatmap for sales
    st.subheader("Quarterly Sales Heatmap")
    fig = go.Figure(data=go.Heatmap(
        z=pivot_sales.drop('Total', axis=1).values,
        x=pivot_sales.drop('Total', axis=1).columns,
        y=pivot_sales.index,
        colorscale='Oranges',
        text=pivot_sales.drop('Total', axis=1).values,
        texttemplate='₱%{text:,.0f}',
        textfont={"size": 12},
        colorbar=dict(title="Sales (₱)")
    ))
    fig.update_layout(
        xaxis_title="Quarter",
        yaxis_title="Year",
        height=max(300, len(pivot_sales) * 50)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Grouped bar chart
    st.subheader("Quarterly Sales Comparison")
    
    plot_data = pivot_sales.drop('Total', axis=1).reset_index()
    plot_data_melted = plot_data.melt(id_vars='year', var_name='Quarter', value_name='Sales')
    
    fig = px.bar(
        plot_data_melted,
        x='year',
        y='Sales',
        color='Quarter',
        barmode='group',
        labels={'year': 'Year', 'Sales': 'Total Sales (₱)'},
        color_discrete_sequence=['#FF6B35', '#FFA500', '#FFD700', '#FFEB3B']
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Year-over-year growth
    st.subheader("Year-over-Year Growth")
    
    if len(pivot_sales) > 1:
        growth_data = []
        years = sorted(pivot_sales.index)
        for i in range(1, len(years)):
            prev_total = pivot_sales.loc[years[i-1], 'Total']
            curr_total = pivot_sales.loc[years[i], 'Total']
            growth_pct = ((curr_total - prev_total) / prev_total * 100) if prev_total != 0 else 0
            growth_data.append({
                'Year': f"{years[i-1]} → {years[i]}",
                'Growth (%)': growth_pct,
                'Previous Sales': prev_total,
                'Current Sales': curr_total
            })
        
        growth_df = pd.DataFrame(growth_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            display_growth = growth_df.copy()
            display_growth['Previous Sales'] = display_growth['Previous Sales'].apply(lambda x: f"₱{x:,.2f}")
            display_growth['Current Sales'] = display_growth['Current Sales'].apply(lambda x: f"₱{x:,.2f}")
            display_growth['Growth (%)'] = display_growth['Growth (%)'].apply(lambda x: f"{x:+.2f}%")
            st.dataframe(display_growth, use_container_width=True, hide_index=True)
        
        with col2:
            fig = px.bar(
                growth_df,
                x='Year',
                y='Growth (%)',
                labels={'Year': 'Period', 'Growth (%)': 'Growth Rate (%)'},
                color='Growth (%)',
                color_continuous_scale=['red', 'yellow', 'green'],
                color_continuous_midpoint=0
            )
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need at least 2 years of data to calculate year-over-year growth.")