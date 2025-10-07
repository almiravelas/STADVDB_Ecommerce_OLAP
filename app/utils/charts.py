import pandas as pd
import plotly.express as px

# Enter design for your charts guyz heree

def create_bar_chart(df: pd.DataFrame, x_axis: str, y_axis: str, title: str):
    if df.empty:
        return None
    fig = px.bar(
        df,
        x=x_axis,
        y=y_axis,
        title=title,
        color=y_axis,
        template="seaborn",
        labels={y_axis: "Total Sales (₱)", x_axis: x_axis.replace("_", " ").title()},
    )
    fig.update_layout(
        xaxis_title=x_axis.replace("_", " ").title(),
        yaxis_title="Sales Amount (₱)",
        title_x=0.5
    )
    return fig
