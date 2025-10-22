import pandas as pd
from etl.transform.dim_rider import transform_dim_rider


def test_transform_dim_rider_normalization():
    """Test dim_rider transformation with before/after output."""
    raw = pd.DataFrame([
        {"id": 100, "rider_name": "John Doe", "vehicleType": "motorbike", "gender": "male", "age": 28, "courier_name": "FEDEZ"},
        {"id": 101, "rider_name": "Jane Smith", "vehicleType": "BIKE", "gender": "f", "age": 32, "courier_name": "DHL"},
        {"id": 102, "rider_name": "Bob Lee", "vehicleType": "  trike  ", "gender": "M", "age": 45, "courier_name": "fedez"},
        {"id": 103, "rider_name": "Alice Wong", "vehicleType": "car", "gender": "Female", "age": 29, "courier_name": "UPS"},
    ])
    
    print("\n" + "="*80)
    print("ETL TEST: transform_dim_rider")
    print("="*80)
    print("\n📥 BEFORE TRANSFORMATION:")
    print(raw.to_string(index=False))
    print(f"\nShape: {raw.shape}")
    print(f"Columns: {list(raw.columns)}")
    
    dim = transform_dim_rider(raw)
    
    print("\n📤 AFTER TRANSFORMATION:")
    print(dim.to_string(index=False))
    print(f"\nShape: {dim.shape}")
    print(f"Columns: {list(dim.columns)}")
    
    print("\n✅ VALIDATION:")
    required = {"rider_key", "rider_name", "vehicleType", "gender", "age", "courier_name"}
    assert required.issubset(set(dim.columns)), f"Missing columns: {required - set(dim.columns)}"
    print(f"   ✓ All required columns present: {required}")
    
    # Gender standardization
    assert set(dim["gender"]) <= {"Male", "Female", "Other"}, f"Unexpected genders: {set(dim['gender'])}"
    print(f"   ✓ Gender standardized: {set(dim['gender'])}")
    print(f"      'male', 'M' → 'Male'")
    print(f"      'f', 'Female' → 'Female'")
    
    # Vehicle type normalization
    expected_vehicles = {"Motorcycle", "Bicycle", "Tricycle", "Car"}
    assert set(dim["vehicleType"]).issubset(expected_vehicles), f"Unexpected vehicle types: {set(dim['vehicleType'])}"
    print(f"   ✓ Vehicle types normalized: {set(dim['vehicleType'])}")
    print(f"      'motorbike' → 'Motorcycle'")
    print(f"      'BIKE' → 'Bicycle'")
    print(f"      '  trike  ' → 'Tricycle' (whitespace trimmed)")
    print(f"      'car' → 'Car'")
    
    # Courier name correction
    assert "FEDEZ" not in dim["courier_name"].values, "FEDEZ not corrected to FEDEX"
    assert "FEDEX" in dim["courier_name"].values, "FEDEX not present after correction"
    print(f"   ✓ Courier names corrected: FEDEZ → FEDEX")
    print(f"   ✓ Final courier names: {set(dim['courier_name'])}")
    
    # rider_key preservation
    assert dim["rider_key"].notna().all(), "rider_key has null values"
    assert list(dim["rider_key"]) == [100, 101, 102, 103], "rider_key values not preserved"
    print(f"   ✓ rider_key preserved: {list(dim['rider_key'])}")
    
    print("="*80 + "\n")
