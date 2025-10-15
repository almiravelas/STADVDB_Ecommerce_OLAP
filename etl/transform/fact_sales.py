import pandas as pd
from .utils import parse_date_formats

# WORK IN PROGRESS

def _calculate_sales_measures(df: pd.DataFrame) -> pd.DataFrame:
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
    df['sales_amount'] = (df['quantity'] * df['unit_price']).round(2)
    return df

def _standardize_sales_date(df: pd.DataFrame) -> pd.DataFrame:
    print("Standardizing date formats...")
    parsed_dates = df['date_key'].apply(parse_date_formats)
    
    # ✅ Create an integer surrogate key (YYYYMMDD)
    df['date_key'] = parsed_dates.dt.strftime('%Y%m%d').astype(int)
    
    # Also keep a proper date column (for analytics or visualization)
    df['full_date'] = parsed_dates.dt.date
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
    df = _standardize_sales_date(df)
    df = _transform_missing_values(df)

    int_columns = ['customer_key', 'product_key', 'rider_key', 'quantity']
    for col in int_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    fact_df = df[[
        'customer_key', 'product_key', 'rider_key', 'date_key',
        'order_number', 'quantity', 'unit_price', 'sales_amount'
    ]]
    
    print("Sales fact table transformed.")
    return fact_df