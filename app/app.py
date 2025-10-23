import streamlit as st
from views import rollup_view, drilldown_view, slice_view, dice_view, pivot_view, explain_view
from utils.db_connection import get_warehouse_engine

st.set_page_config(
    page_title="Shopee OLAP Analytics",
    page_icon="🧡",
    layout="wide"
)

# Custom CSS for medium-wide layout and borders
st.markdown("""
    <style>
    .block-container {
        max-width: 1200px;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Light mode styles (default) */
    div[data-testid="stMetric"] {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px;
        background-color: #fafafa;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 8px;
    }
    div.stPlotlyChart {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 8px;
        background-color: white;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
    }
    
    /* Dark mode styles */
    @media (prefers-color-scheme: dark) {
        div[data-testid="stMetric"] {
            border: 1px solid #404040;
            background-color: #1e1e1e;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid #404040;
        }
        div.stPlotlyChart {
            border: 1px solid #404040;
            background-color: #0e1117;
        }
        div[data-testid="stExpander"] {
            border: 1px solid #404040;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧡 Shopee OLAP Analytics Dashboard")

engine = get_warehouse_engine()

# Create tabs for OLAP operations
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "▣ Roll-up",
    "▤ Drill-down",
    "▥ Slice",
    "▦ Dice",
    "▧ Pivot"
])

#with tab1:
   # explain_view.show_explain_view(engine)

with tab1:
   rollup_view.show_rollup_view(engine)

with tab2:
    drilldown_view.show_drilldown_view(engine)
    
with tab3:
    slice_view.show_slice_view(engine)
    
with tab4:
    dice_view.show_dice_view(engine)

with tab5:
    pivot_view.show_pivot_view(engine)