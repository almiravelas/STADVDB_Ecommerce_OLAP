import os
import pandas as pd
from .utils import standardize_gender, parse_date_formats


def transform_dim_user(df: pd.DataFrame) -> pd.DataFrame:
    """Transforms raw user data into a user dimension table with continent mapping from users.csv."""
    if df is None:
        return None

    print("Transforming user data...")
    df = df.copy()

    # --- Rename id to user_key ---
    if 'id' in df.columns:
        df.rename(columns={'id': 'user_key'}, inplace=True)
    if 'user_key' not in df.columns:
        df['user_key'] = df.index + 1

    # --- Fill missing required fields ---
    for col in ['username', 'city', 'country']:
        if col not in df.columns:
            df[col] = 'Unknown'

    # --- Standardize gender ---
    df['gender'] = standardize_gender(df['gender'].astype(str)) if 'gender' in df.columns else 'Other'

    # --- Full name ---
    first = df.get('firstName', '').fillna('')
    last = df.get('lastName', '').fillna('')
    df['full_name'] = (first.astype(str) + ' ' + last.astype(str)).str.strip().replace('', 'Unknown')

    # --- Normalize capitalization ---
    for col in ['city', 'country']:
        df[col] = df[col].fillna('Unknown').replace('', 'Unknown').astype(str).str.title()

    # --- Load mapping from users.csv ---
    csv_path = os.path.join(os.path.dirname(__file__), "users.csv")

    if os.path.exists(csv_path):
        try:
            mapping_df = pd.read_csv(csv_path)
            mapping_df.columns = mapping_df.columns.str.lower().str.strip()

            # Expect columns like: country, region OR country, continent
            country_col = "country"
            continent_col = "region" if "region" in mapping_df.columns else "continent"

            mapping_df[country_col] = mapping_df[country_col].astype(str).str.title()
            mapping_df[continent_col] = mapping_df[continent_col].astype(str).str.title()

            # Merge with the main DataFrame
            df = df.merge(
                mapping_df[[country_col, continent_col]].drop_duplicates(),
                how="left",
                left_on="country",
                right_on=country_col
            )

            # Fill continent from mapping or set fallback
            df["continent"] = df[continent_col].fillna("Other")
            df.drop(columns=[country_col, continent_col], errors="ignore", inplace=True)

            print(f"✅ Loaded custom mapping from {csv_path}")
        except Exception as e:
            print(f"⚠️ Failed to load custom mapping file: {e}")
            df["continent"] = "Other"
    else:
        print("⚠️ users.csv not found — using built-in default mapping.")
        country_to_continent = {
            'Philippines': 'Asia', 'Japan': 'Asia', 'China': 'Asia', 'India': 'Asia',
            'Singapore': 'Asia', 'South Korea': 'Asia', 'Indonesia': 'Asia',
            'Thailand': 'Asia', 'Malaysia': 'Asia', 'Vietnam': 'Asia', 'Taiwan': 'Asia',
            'Hong Kong': 'Asia', 'Pakistan': 'Asia', 'Bangladesh': 'Asia',
            'United Kingdom': 'Europe', 'Germany': 'Europe', 'France': 'Europe',
            'Spain': 'Europe', 'Italy': 'Europe', 'Netherlands': 'Europe',
            'Poland': 'Europe', 'Sweden': 'Europe', 'Norway': 'Europe',
            'United States': 'North America', 'Canada': 'North America', 'Mexico': 'North America',
            'Brazil': 'South America', 'Argentina': 'South America', 'Chile': 'South America',
            'Peru': 'South America', 'Colombia': 'South America',
            'Australia': 'Oceania', 'New Zealand': 'Oceania',
            'South Africa': 'Africa', 'Nigeria': 'Africa', 'Egypt': 'Africa', 'Kenya': 'Africa'
        }
        df["continent"] = df["country"].map(country_to_continent).fillna("Other")

    # --- Handle signup_date ---
    if "createdAt" in df.columns and "signup_date" not in df.columns:
        df.rename(columns={"createdAt": "signup_date"}, inplace=True)

    df["signup_date"] = df.get("signup_date", pd.NaT)
    df["signup_date"] = df["signup_date"].apply(
        lambda x: parse_date_formats(x) if isinstance(x, str) else pd.to_datetime(x, errors="coerce")
    )

    # --- Deduplicate ---
    df.sort_values(by=["user_key", "signup_date"], inplace=True)
    df.drop_duplicates(subset="user_key", keep="last", inplace=True)

    # --- Final dimension output ---
    dim_df = df[["user_key", "username", "full_name", "gender", "city", "country", "continent", "signup_date"]]

    print("User dimension transformed.")
    return dim_df.reset_index(drop=True)
