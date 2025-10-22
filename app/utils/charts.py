import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Enter design for your charts guyz heree

def create_bar_chart(df: pd.DataFrame, x_axis: str, y_axis: str, title: str, color: str = None):
    """
    Creates a bar chart.
    - If 'color' is None (default), colors bars by the y-axis value (gradient).
    - If 'color' is a column name, colors bars by that column (grouped).
    """
    if df.empty:
        return None
    
    # --- MODIFICATION ---
    # Use the 'color' param if provided, otherwise default to y_axis
    color_param = color if color else y_axis
    # --- END MODIFICATION ---

    fig = px.bar(
        df,
        x=x_axis,
        y=y_axis,
        title=title,
        color=color_param, # <-- Use the modified color parameter
        template="seaborn",
        labels={y_axis: "Total Sales (₱)", x_axis: x_axis.replace("_", " ").title()},
    )
    fig.update_layout(
        xaxis_title=x_axis.replace("_", " ").title(),
        yaxis_title="Sales Amount (₱)",
        title_x=0.5
    )
    return fig

def create_multi_metric_bar_chart(df: pd.DataFrame, x_axis: str, metrics: list, title: str):
    """Create a grouped bar chart for multiple metrics"""
    if df.empty:
        return None
    
    fig = go.Figure()
    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']
    
    for i, metric in enumerate(metrics):
        fig.add_trace(go.Bar(
            name=metric.replace('_', ' ').title(),
            x=df[x_axis],
            y=df[metric],
            marker_color=colors[i % len(colors)]
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_axis.replace("_", " ").title(),
        yaxis_title="Value",
        barmode='group',
        template="seaborn",
        title_x=0.5,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def create_pie_chart(df: pd.DataFrame, names: str, values: str, title: str):
    """Create a pie chart for distribution analysis"""
    if df.empty:
        return None
    
    fig = px.pie(
        df,
        names=names,
        values=values,
        title=title,
        template="seaborn",
        hole=0.3  # Makes it a donut chart
    )
    fig.update_layout(title_x=0.5)
    return fig

def create_line_chart(df: pd.DataFrame, x_axis: str, y_axis: str, title: str, color=None):
    """Create a line chart for trend analysis"""
    if df.empty:
        return None
    
    fig = px.line(
        df,
        x=x_axis,
        y=y_axis,
        title=title,
        color=color,
        template="seaborn",
        markers=True
    )
    fig.update_layout(
        xaxis_title=x_axis.replace("_", " ").title(),
        yaxis_title=y_axis.replace("_", " ").title(),
        title_x=0.5
    )
    return fig

def create_heatmap(pivot_df: pd.DataFrame, title: str):
    """Create a heatmap from pivoted data"""
    if pivot_df.empty:
        return None
    
    fig = px.imshow(
        pivot_df,
        title=title,
        template="seaborn",
        aspect="auto",
        color_continuous_scale="RdYlGn"
    )
    fig.update_layout(title_x=0.5)
    return fig