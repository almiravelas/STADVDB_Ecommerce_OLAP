import streamlit as st
from views import dashboard_view, rider_view, product_view, user_view

st.set_page_config(
    page_title="Shopee Sales Dashboard",
    layout="wide",
    page_icon="🧡"
)

st.title("🧡 Shopee Sales Dashboard")

tab1, tab2, tab3, tab4 = st.tabs([
    "Dashboard",
    "Product Analysis",
    "User Analysis",
    "Rider Performance"
])

with tab1:
    dashboard_view.show_dashboard()

with tab2:
    product_view.show_product_view()

with tab3:
    user_view.show_user_view()
    
with tab4:
    rider_view.show_rider_view()
