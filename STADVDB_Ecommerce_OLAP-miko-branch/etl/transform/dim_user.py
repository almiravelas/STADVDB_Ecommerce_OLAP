import pandas as pd
from .utils import standardize_gender, parse_date_formats

def transform_dim_user(df: pd.DataFrame) -> pd.DataFrame:
    """Transforms raw user data into a user dimension table."""
    if df is None:
        return None

    print("Transforming user data...")

    # rename id to user_key
    df.rename(columns={'id': 'user_key'}, inplace=True)

    # standardize gender using shared utility function
    df['gender'] = standardize_gender(df['gender'])

    # create full_name column
    df['full_name'] = (df['firstName'].fillna('') + ' ' + df['lastName'].fillna('')).str.strip()

    # normalize capitalization for city and country
    for col in ['city', 'country']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.title()

    # rename createdAt to signup_date
    if 'createdAt' in df.columns:
        df.rename(columns={'createdAt': 'signup_date'}, inplace=True)

    # standardize date formats for signup_date
    if 'signup_date' in df.columns:
        df['signup_date'] = df['signup_date'].apply(parse_date_formats)

    # select final columns for the dimension table
    dim_df = df[['user_key', 'username', 'full_name', 'gender', 'city', 'country', 'signup_date']]

    print("User dimension transformed.")
    return dim_df
