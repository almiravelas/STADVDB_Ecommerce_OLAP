import pandas as pd
from .utils import parse_date_formats

# WORK IN PROGRESS

def _calculate_sales_measures(df: pd.DataFrame) -> pd.DataFrame:
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
    df['sales_amount'] = (df['quantity'] * df['unit_price']).round(2)
    return df

def _standardize_sales_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parses various date formats and converts them to an integer key (YYYYMMDD)
    to match the dim_date primary key.
    """
    print("Standardizing date formats to YYYYMMDD integer key...")

    # 1. Parse various string formats into proper datetime objects
    parsed_dates = df['date_key'].apply(parse_date_formats)

    # 2. Convert datetime objects to a YYYYMMDD string, coercing errors to NaT
    #    Then convert to a numeric type, which turns NaT into NaN
    date_keys_numeric = pd.to_numeric(parsed_dates.dt.strftime('%Y%m%d'), errors='coerce')

    # 3. Fill any resulting NaN values with 0 and cast to a non-nullable integer
    df['date_key'] = date_keys_numeric.fillna(0).astype(int)
    
    return df

def _transform_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = ['quantity', 'unit_price', 'sales_amount']
    for col in numeric_cols:
        if df[col].isnull().any():
            mean_val = df[col].mean()
            df[col] = df[col].fillna(mean_val)
            print(f"Filled NaN in '{col}' with mean value: {mean_val:.2f}")

    key_cols = ['customer_key', 'product_key', 'rider_key']
    df.dropna(subset=key_cols, inplace=True)
    return df

# WORK IN PROGRESS

def transform_fact_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Transforms raw sales data into a sales fact table."""
    if df is None:
        return None

    print("\nTransforming sales data...")

    df.rename(columns={
        'userId': 'customer_key',
        'ProductId': 'product_key',
        'deliveryRiderId': 'rider_key',
        'deliveryDate': 'date_key',
        'price': 'unit_price',
        'orderNumber': 'order_number'
    }, inplace=True)

    df = _calculate_sales_measures(df)
    df = _standardize_sales_date(df) # 👈 This function is now updated
    df = _transform_missing_values(df)

    # Add 'date_key' to the list of columns to be converted to integer
    int_columns = ['customer_key', 'product_key', 'rider_key', 'date_key', 'quantity'] # 👈 ADDED 'date_key'
    for col in int_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    fact_df = df[[
        'customer_key', 'product_key', 'rider_key', 'date_key',
        'order_number', 'quantity', 'unit_price', 'sales_amount'
    ]]
    
    print("Sales fact table transformed.")
    return fact_df