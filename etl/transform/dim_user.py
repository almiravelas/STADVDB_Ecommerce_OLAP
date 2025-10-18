import pandas as pd
from .utils import standardize_gender, parse_date_formats


def transform_dim_user(df: pd.DataFrame) -> pd.DataFrame:
    """Transforms raw user data into a user dimension table."""
    if df is None:
        return None

    print("Transforming user data...")
    df = df.copy()

    # rename id to user_key
    if 'id' in df.columns:
        df.rename(columns={'id': 'user_key'}, inplace=True)
    if 'user_key' not in df.columns:
        df['user_key'] = df.index + 1

    required_defaults = {
        'username': 'Unknown',
        'city': 'Unknown',
        'country': 'Unknown'
    }
    for col, default in required_defaults.items():
        if col not in df.columns:
            df[col] = default

    # standardize gender
    if 'gender' in df.columns:
        df['gender'] = df['gender'].astype(str)
        df['gender'] = standardize_gender(df['gender'])
    else:
        df['gender'] = 'Other'

    # create full_name
    first = df['firstName'].fillna('') if 'firstName' in df.columns else pd.Series([''] * len(df), index=df.index)
    last = df['lastName'].fillna('') if 'lastName' in df.columns else pd.Series([''] * len(df), index=df.index)
    first = first.astype(str)
    last = last.astype(str)
    df['full_name'] = (first + ' ' + last).str.strip()
    df['full_name'] = df['full_name'].replace('', 'Unknown')

    # normalize capitalization for city/country
    for col in ['city', 'country']:
        df[col] = df[col].fillna('Unknown').replace('', 'Unknown')
        df[col] = df[col].astype(str).str.title()

    country_to_region = {
        # Asia
        'Philippines': 'Asia',
        'Japan': 'Asia',
        'China': 'Asia',
        'India': 'Asia',
        'Singapore': 'Asia',
        'South Korea': 'Asia',
        'Indonesia': 'Asia',
        'Thailand': 'Asia',
        'Malaysia': 'Asia',
        'Vietnam': 'Asia',

        # Europe
        'United Kingdom': 'Europe',
        'Germany': 'Europe',
        'France': 'Europe',
        'Spain': 'Europe',
        'Italy': 'Europe',
        'Netherlands': 'Europe',
        'Sweden': 'Europe',
        'Poland': 'Europe',

        # North America
        'United States': 'North America',
        'Canada': 'North America',
        'Mexico': 'North America',

        # Oceania
        'Australia': 'Oceania',
        'New Zealand': 'Oceania',

        # South America
        'Brazil': 'South America',
        'Argentina': 'South America',
        'Chile': 'South America',

        # Africa
        'South Africa': 'Africa',
        'Nigeria': 'Africa',
        'Egypt': 'Africa'
    }

    df['region'] = df['country'].map(country_to_region).fillna('Other')

    if 'createdAt' in df.columns and 'signup_date' not in df.columns:
        df.rename(columns={'createdAt': 'signup_date'}, inplace=True)

    if 'signup_date' in df.columns:
        df['signup_date'] = df['signup_date'].apply(
            lambda value: parse_date_formats(value) if isinstance(value, str) else pd.to_datetime(value, errors='coerce')
        )
    else:
        df['signup_date'] = pd.NaT

    if 'user_key' in df.columns:
        df.sort_values(by=['user_key', 'signup_date'], inplace=True)
        df = df.drop_duplicates(subset='user_key', keep='last')

    dim_df = df[['user_key', 'username', 'full_name', 'gender', 'city', 'country', 'region', 'signup_date']]

    print("User dimension transformed.")
    return dim_df.reset_index(drop=True)
