import pandas as pd
import streamlit as st
from sqlalchemy.engine import Engine

@st.cache_data
def get_product_data(_engine: Engine) -> pd.DataFrame:
    if  pd.DataFrame is None:
        return None
    pass
    return pd.DataFrame
