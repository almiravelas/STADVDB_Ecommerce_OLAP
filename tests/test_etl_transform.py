import pandas as pd
import datetime as dt

from etl.transform.dim_user import transform_dim_user
from etl.transform.fact_sales import transform_fact_sales
from etl.transform.dim_date import transform_dim_date


def test_transform_dim_user_minimal_columns():
    """Test dim_user transformation with before/after output."""
    raw = pd.DataFrame([
        {"id": 1, "username": "u1", "firstName": "A", "lastName": "AA", "gender": "Male", "city": "Manila", "country": "Philippines", "createdAt": "2021-01-01"},
        {"id": 2, "username": "u2", "firstName": "B", "lastName": "BB", "gender": "female", "city": "tokyo", "country": "japan", "createdAt": "2022-06-15"},
        {"id": 3, "username": "u3", "firstName": "C", "lastName": "CC", "gender": "m", "city": "BERLIN", "country": "Germany", "createdAt": "05/20/2023"},
    ])
    
    print("\n" + "="*80)
    print("ETL TEST: transform_dim_user")
    print("="*80)
    print("\n📥 BEFORE TRANSFORMATION:")
    print(raw.to_string(index=False))
    print(f"\nShape: {raw.shape}")
    print(f"Columns: {list(raw.columns)}")
    
    dim = transform_dim_user(raw)
    
    print("\n📤 AFTER TRANSFORMATION:")
    print(dim.to_string(index=False))
    print(f"\nShape: {dim.shape}")
    print(f"Columns: {list(dim.columns)}")
    
    print("\n✅ VALIDATION:")
    required = {"user_key", "continent", "country", "city", "gender", "signup_date", "full_name", "username"}
    assert required.issubset(set(dim.columns)), f"Missing columns: {required - set(dim.columns)}"
    print(f"   ✓ All required columns present: {required}")
    
    assert dim["user_key"].notna().all(), "user_key has null values"
    print(f"   ✓ user_key non-null")
    
    # Gender standardized capitalization
    assert set(dim["gender"]) <= {"Male", "Female", "Other"}, f"Unexpected genders: {set(dim['gender'])}"
    print(f"   ✓ Gender standardized: {set(dim['gender'])}")
    
    # Full name assembled
    assert (dim["full_name"].str.len() > 0).all(), "Empty full_name found"
    print(f"   ✓ Full names assembled: {list(dim['full_name'])}")
    
    # Continent mapping
    assert dim["continent"].notna().all(), "continent has null values"
    print(f"   ✓ Continents mapped: {list(dim['continent'])}")
    
    # City/country normalized
    assert all(dim["city"].str[0].str.isupper()), "City not title-cased"
    assert all(dim["country"].str[0].str.isupper()), "Country not title-cased"
    print(f"   ✓ City/country normalized to title case")
    
    print("="*80 + "\n")


def test_transform_fact_sales_computed_and_renamed():
    """Test fact_sales transformation with before/after output."""
    raw = pd.DataFrame([
        {"quantity": 2, "price": 50.0, "orderNumber": "ORD-1", "userId": 1, "ProductId": 10, "deliveryRiderId": 100, "deliveryDate": "2021-01-02"},
        {"quantity": 3, "price": 20.0, "orderNumber": "ORD-2", "userId": 2, "ProductId": 11, "deliveryRiderId": 101, "deliveryDate": "2021-01-03"},
        {"quantity": 5, "price": 15.5, "orderNumber": "ORD-3", "userId": 1, "ProductId": 12, "deliveryRiderId": 100, "deliveryDate": "05/10/2021"},
    ])
    
    print("\n" + "="*80)
    print("ETL TEST: transform_fact_sales")
    print("="*80)
    print("\n📥 BEFORE TRANSFORMATION:")
    print(raw.to_string(index=False))
    print(f"\nShape: {raw.shape}")
    print(f"Columns: {list(raw.columns)}")
    
    fact = transform_fact_sales(raw)
    
    print("\n📤 AFTER TRANSFORMATION:")
    print(fact.to_string(index=False))
    print(f"\nShape: {fact.shape}")
    print(f"Columns: {list(fact.columns)}")
    
    print("\n✅ VALIDATION:")
    # Must have computed amount and renamed fields for OLAP queries
    required = {"sales_amount", "order_number", "customer_key", "date_key", "unit_price"}
    assert required.issubset(set(fact.columns)), f"Missing columns: {required - set(fact.columns)}"
    print(f"   ✓ All required columns present: {required}")
    
    # Validate computation
    m = {row["order_number"]: row["sales_amount"] for _, row in fact.iterrows()}
    assert m["ORD-1"] == 2 * 50.0, f"ORD-1 sales_amount incorrect: {m['ORD-1']} != {2*50.0}"
    assert m["ORD-2"] == 3 * 20.0, f"ORD-2 sales_amount incorrect: {m['ORD-2']} != {3*20.0}"
    assert m["ORD-3"] == 5 * 15.5, f"ORD-3 sales_amount incorrect: {m['ORD-3']} != {5*15.5}"
    print(f"   ✓ sales_amount computed correctly:")
    print(f"      ORD-1: 2 × 50.0 = {m['ORD-1']}")
    print(f"      ORD-2: 3 × 20.0 = {m['ORD-2']}")
    print(f"      ORD-3: 5 × 15.5 = {m['ORD-3']}")
    
    # Validate normalized integer date_key
    assert fact["date_key"].dtype.kind in {"i", "u"}, f"date_key not integer: {fact['date_key'].dtype}"
    print(f"   ✓ date_key is integer type: {fact['date_key'].dtype}")
    
    assert set(len(str(v)) for v in fact["date_key"]) == {8}, f"date_key not YYYYMMDD: {list(fact['date_key'])}"
    print(f"   ✓ date_key format YYYYMMDD: {list(fact['date_key'])}")
    
    # Validate renames
    assert "customer_key" in fact.columns and fact["customer_key"].notna().all()
    print(f"   ✓ userId → customer_key: {list(fact['customer_key'])}")
    
    assert "product_key" in fact.columns and fact["product_key"].notna().all()
    print(f"   ✓ ProductId → product_key: {list(fact['product_key'])}")
    
    assert "rider_key" in fact.columns and fact["rider_key"].notna().all()
    print(f"   ✓ deliveryRiderId → rider_key: {list(fact['rider_key'])}")
    
    print("="*80 + "\n")


def test_transform_dim_date_derivations():
    """Test dim_date transformation with before/after output."""
    raw = pd.DataFrame({"full_date": pd.to_datetime(["2020-01-01", "2020-02-15", "2021-03-20", "2021-12-25"])})
    
    print("\n" + "="*80)
    print("ETL TEST: transform_dim_date")
    print("="*80)
    print("\n📥 BEFORE TRANSFORMATION:")
    print(raw.to_string(index=False))
    print(f"\nShape: {raw.shape}")
    print(f"Columns: {list(raw.columns)}")
    
    date_dim = transform_dim_date(raw)
    
    print("\n📤 AFTER TRANSFORMATION:")
    print(date_dim.to_string(index=False))
    print(f"\nShape: {date_dim.shape}")
    print(f"Columns: {list(date_dim.columns)}")
    
    print("\n✅ VALIDATION:")
    # Common derivations needed by date OLAP (year, month_name)
    required = {"full_date", "year", "month_name", "day_name", "date_key", "is_weekend"}
    assert required.issubset(set(date_dim.columns)), f"Missing columns: {required - set(date_dim.columns)}"
    print(f"   ✓ All required columns present: {required}")
    
    # Year correctness
    by_date = {str(r["full_date"])[:10]: r["year"] for _, r in date_dim.iterrows()}
    assert by_date["2020-01-01"] == 2020, f"Year incorrect for 2020-01-01"
    assert by_date["2021-03-20"] == 2021, f"Year incorrect for 2021-03-20"
    print(f"   ✓ Year extracted correctly: {list(date_dim['year'])}")
    
    # Month name
    print(f"   ✓ Month names: {list(date_dim['month_name'])}")
    
    # Day name
    print(f"   ✓ Day names: {list(date_dim['day_name'])}")
    
    # Weekend flag for 2020-02-15 (Saturday)
    weekend_row = date_dim[date_dim["full_date"].dt.date.astype(str) == "2020-02-15"].iloc[0]
    assert weekend_row["is_weekend"] == "Y", f"2020-02-15 (Saturday) should be weekend"
    print(f"   ✓ Weekend flag correct: 2020-02-15 (Saturday) = 'Y'")
    
    # date_key format
    assert date_dim["date_key"].dtype.kind in {"i", "u"}, f"date_key not integer"
    print(f"   ✓ date_key is integer YYYYMMDD: {list(date_dim['date_key'])}")
    
    print("="*80 + "\n")
