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
st.markdown("""
This dashboard demonstrates **OLAP (Online Analytical Processing)** operations on e-commerce sales data.
Explore different perspectives of the data using various analytical operations.
""")

# Sidebar for cache management
with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown("---")
    
    st.subheader("🔄 Cache Management")
    st.caption("Cached queries improve performance by storing recent results.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🗑️ Clear Query Cache", use_container_width=True):
            st.cache_data.clear()
            st.success("✅ Cache cleared!")
            st.rerun()
    with col2:
        if st.button("ℹ️", use_container_width=True, help="Cache Information"):
            st.info("""
            **Cache Info:**
            - Query Results: 5 min TTL
            - Lookups: 10 min TTL
            - Connection: Persistent
            """)
    
    st.markdown("---")
    
    # Cache performance indicator
    st.subheader("📊 Performance")
    st.caption("Queries execute faster when cached (< 0.05s = cached)")
    
    st.markdown("---")
    st.caption("💡 **Tip:** First query hits database, subsequent queries use cache for 5 minutes.")

engine = get_warehouse_engine()

# Create tabs for OLAP operations
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍 EXPLAIN",
    "▣ Roll-up",
    "▤ Drill-down",
    "▥ Slice",
    "▦ Dice",
    "▧ Pivot"
])

with tab1:
    explain_view.show_explain_view(engine)

with tab2:
   rollup_view.show_rollup_view(engine)

with tab3:
    drilldown_view.show_drilldown_view(engine)
    
with tab4:
    slice_view.show_slice_view(engine)
    
with tab5:
    dice_view.show_dice_view(engine)

with tab6:
    pivot_view.show_pivot_view(engine)