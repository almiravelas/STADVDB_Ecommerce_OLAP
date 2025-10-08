import streamlit as st
from utils.db_connection import get_warehouse_engine
from queries.user_queries import get_user_data

def show_user_view():
    st.title("User Dimension")
    engine = get_warehouse_engine()
    df = get_user_data(engine)
    if df.empty:
        st.warning("WALAA PAAAA")
