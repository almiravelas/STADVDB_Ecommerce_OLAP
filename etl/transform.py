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


def transform_fact_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Transforms raw sales data into a sales fact table."""
    if df is None:
        return None

    print("Transforming sales data...")

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
        df[col] = df[col].astype(int)

    fact_df = df[[
        'customer_key',
        'product_key',
        'rider_key',
        'date_key',
        'order_number',
        'quantity',
        'unit_price',
        'sales_amount'
    ]]

    print("Sales fact table transformed.")
    return fact_df

def _calculate_sales_measures(df: pd.DataFrame) -> pd.DataFrame:
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
    
    df['sales_amount'] = (df['quantity'] * df['unit_price']).round(2)
    return df

def _standardize_sales_date(df: pd.DataFrame) -> pd.DataFrame:
    df['date_key'] = pd.to_datetime(df['date_key'], errors='coerce').dt.strftime('%Y-%m-%d')
    return df

def _transform_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    # impute - mean
    # add more cols
    numeric_cols = ['quantity', 'unit_price', 'sales_amount']
    for col in numeric_cols:
        if df[col].isnull().any():
            mean_val = df[col].mean()
            # FIX: Reassign the result instead of using inplace=True
            df[col] = df[col].fillna(mean_val)
            print(f"Filled NaN in '{col}' with mean value: {mean_val:.2f}")

    # impute - mode
    if df['date_key'].isnull().any():
        mode_val = df['date_key'].mode()[0]
        # FIX: Reassign the result instead of using inplace=True
        df['date_key'] = df['date_key'].fillna(mode_val)
        print(f"Filled NaN in 'date_key' with mode value: {mode_val}")

    # drops missing keys
    key_cols = ['customer_key', 'product_key', 'rider_key']
    df.dropna(subset=key_cols, inplace=True)
    
    return df