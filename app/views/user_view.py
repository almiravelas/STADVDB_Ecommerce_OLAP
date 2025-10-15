import streamlit as st
from utils.db_connection import get_warehouse_engine
from queries.user_queries import get_user_data

@st.cache_data(ttl=600)
def load_user_data(_engine):
    return get_user_data(_engine)

def show_user_view(engine):
    st.title("User Dimension")
    df = load_user_data(engine)
    if df.empty:
        st.warning("WALAA PAAAA")
