import pandas as pd

# transform GENDER columns
def standardize_gender(series: pd.Series) -> pd.Series:
    gender_map = {
        'm': 'Male',
        'male': 'Male',
        'f': 'Female',
        'female': 'Female'
    }
    
    standardized_series = series.str.lower().map(gender_map)
    return standardized_series.fillna('Other')

# transform DATE columns

# transform CATEGORY column from PRODUCTS

# transform dateOfBirth from USERS

# ---

# dimension rider (Aza)
def transform_dim_rider(df: pd.DataFrame) -> pd.DataFrame:
    """Transforms raw rider data into a rider dimension table."""
    if df is None:
        return None
    
    print("Transforming rider data...")
    
    df.rename(columns={'id': 'rider_key'}, inplace=True)
    df['gender'] = standardize_gender(df['gender'])
    
    # typo FEDEZ to FEDEX
    df['courier_name'] = df['courier_name'].str.replace('FEDEZ', 'FEDEX')
    
    dim_df = df[['rider_key', 'rider_name', 'vehicleType', 'gender', 'age', 'courier_name']]
    
    print("Rider dimension transformed.")
    return dim_df

def transform_dim_customer(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        return None
    
    pass # remove when done
    return df

def transform_dim_product(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        return None
    pass
    return df

def transform_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        return None
    pass
    return df

def transform_fact_sales(
    orders_df: pd.DataFrame, 
    orderitems_df: pd.DataFrame, 
    dim_customer_df: pd.DataFrame, 
    dim_product_df: pd.DataFrame,
    dim_date_df: pd.DataFrame
) -> pd.DataFrame:
    pass
    return pd.DataFrame() # wala pa for now