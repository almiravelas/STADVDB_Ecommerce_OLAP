import streamlit as st
from utils.db_connection import get_warehouse_engine
from queries.product_queries import get_product_data

def show_product_view():
    st.title("Product Analysis")
    engine = get_warehouse_engine()
    df = get_product_data(engine)
    if df.empty:
        st.warning("WALA PAAAAA")
