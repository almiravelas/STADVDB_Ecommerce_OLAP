import pandas as pd
from .utils import standardize_gender

def transform_dim_rider(df: pd.DataFrame) -> pd.DataFrame:
    """Transforms raw rider data into a rider dimension table."""
    if df is None:
        return None
    
    print("Transforming rider data...")

    df.rename(columns={'id': 'rider_key'}, inplace=True)

    df['gender'] = standardize_gender(df['gender'])

    # FEDEZ → FEDEX
    df['courier_name'] = df['courier_name'].str.replace('FEDEZ', 'FEDEX', case=False)

    vehicle_map = {
        'motorbike': 'Motorcycle',
        'bike': 'Bicycle',
        'trike': 'Tricycle',
        'car': 'Car',
    }

    df['vehicleType'] = (
        df['vehicleType']
        .str.strip()
        .str.lower()
        .replace(vehicle_map)
        .str.capitalize() 
    )

    dim_df = df[['rider_key', 'rider_name', 'vehicleType', 'gender', 'age', 'courier_name']]

    print("Rider dimension transformed with standardized vehicle types.")
    return dim_df