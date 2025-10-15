import streamlit as st
from views import dashboard_view, rider_view, product_view, user_view, date_view
from utils.db_connection import get_warehouse_engine

st.set_page_config(
    page_title="Shopee Sales Dashboard",
    layout="wide",
    page_icon="🧡"
)

st.title("🧡 Shopee Sales Dashboard")

engine = get_warehouse_engine() 

engine = get_warehouse_engine() 

tab1, tab2, tab3, tab4, tab5= st.tabs([
    "Dashboard",
    "Product Analysis",
    "User Analysis",
    "Rider Performance",
    "Date Analysis"
])

with tab1:
    dashboard_view.show_dashboard(engine)

with tab2:
    product_view.show_product_view(engine)

with tab3:
    user_view.show_user_view(engine)
    
with tab4:
    rider_view.show_rider_view(engine)
    
with tab5:
    date_view.show_date_view()
