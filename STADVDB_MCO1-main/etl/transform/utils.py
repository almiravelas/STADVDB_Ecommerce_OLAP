# you can use these functions in your transformations para di paulit ulit :P
import pandas as pd

def standardize_gender(series: pd.Series) -> pd.Series:
    """Standardizes gender strings to 'Male', 'Female', or 'Other'."""
    gender_map = {
        'm': 'Male',
        'male': 'Male',
        'f': 'Female',
        'female': 'Female'
    }
    
    standardized_series = series.str.lower().map(gender_map)
    return standardized_series.fillna('Other')

def parse_date_formats(date_str: str) -> pd.Timestamp:
    """
    Tries to parse a date string using a list of expected formats.
    Returns a Timestamp on success or NaT (Not a Time) on failure.
    """
    if not isinstance(date_str, str):
        return pd.NaT

    date_formats = [
        '%Y-%m-%d',  # e.g., 2025-05-24
        '%m/%d/%Y',  # e.g., 06/25/2025
        '%m-%d-%Y'   # e.g., 10-30-2024
    ]
    for fmt in date_formats:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except (ValueError, TypeError):
            pass
    return pd.NaT