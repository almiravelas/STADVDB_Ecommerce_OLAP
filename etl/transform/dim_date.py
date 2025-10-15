import pandas as pd

def transform_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms a DataFrame containing a column 'full_date'
    into a properly structured dimension_Date table.
    """
    if df is None or df.empty:
        return None

    # Ensure full_date is a datetime
    df['full_date'] = pd.to_datetime(df['full_date'])

    # Derive fields
    df['date_key'] = df['full_date'].dt.strftime('%Y%m%d').astype(int)
    df['day_name'] = df['full_date'].dt.day_name()
    df['month_name'] = df['full_date'].dt.month_name()
    df['day'] = df['full_date'].dt.day
    df['month'] = df['full_date'].dt.month
    df['year'] = df['full_date'].dt.year
    df['is_weekend'] = df['full_date'].dt.dayofweek.isin([5, 6]).map({True: "Y", False: "N"})

    # Reorder columns
    df = df[['date_key', 'full_date', 'day_name', 'month_name', 'day', 'month', 'year', 'is_weekend']]

    return df