import pandas as pd
from etl.transform.dim_product import transform_dim_product


def test_transform_dim_product_normalization():
    """Test dim_product transformation with before/after output."""
    raw = pd.DataFrame([
        {"ID": 1, "Name": "  Phone  ", "Category": "GADGETS", "Description": "Smartphone", "ProductCode": "P001", "Price": 500.0, "CreatedAt": "2024-01-01", "UpdatedAt": "2024-02-01"},
        {"ID": 2, "Name": "Laptop", "Category": "Electronics", "Description": "Gaming laptop", "ProductCode": "P002", "Price": 1200.0, "CreatedAt": "2024-02-01", "UpdatedAt": "2024-03-01"},
        {"ID": 3, "Name": "Toy Car", "Category": "Toy", "Description": "Small car", "ProductCode": "P003", "Price": 15.0, "CreatedAt": "2024-03-01", "UpdatedAt": "2024-04-01"},
        {"ID": 4, "Name": "Makeup Kit", "Category": "make up", "Description": None, "ProductCode": "P004", "Price": 25.0, "CreatedAt": "2024-03-02", "UpdatedAt": "2024-04-02"},
        {"ID": 5, "Name": "Bagpack", "Category": "BAG", "Description": "Travel bag", "ProductCode": "P005", "Price": 60.0, "CreatedAt": "2024-03-03", "UpdatedAt": "2024-04-03"},
        {"ID": 6, "Name": "BAG", "Category": "bag", "Description": "Handbag", "ProductCode": "P005", "Price": 55.0, "CreatedAt": "2024-03-03", "UpdatedAt": "2024-04-04"},  # duplicate P005
    ])
    
    print("\n" + "="*80)
    print("ETL TEST: transform_dim_product")
    print("="*80)
    print("\n📥 BEFORE TRANSFORMATION:")
    print(raw.to_string(index=False))
    print(f"\nShape: {raw.shape}")
    print(f"Columns: {list(raw.columns)}")
    
    dim = transform_dim_product(raw)
    
    print("\n📤 AFTER TRANSFORMATION:")
    print(dim.to_string(index=False))
    print(f"\nShape: {dim.shape}")
    print(f"Columns: {list(dim.columns)}")
    
    print("\n✅ VALIDATION:")
    required = {"product_key", "product_name", "category", "product_code", "price"}
    assert required.issubset(set(dim.columns)), f"Missing columns: {required - set(dim.columns)}"
    print(f"   ✓ All required columns present: {required}")
    
    # Deduplication check
    assert len(dim) < len(raw), "Duplicates not removed"
    assert dim["product_code"].is_unique, "product_code not unique after dedup"
    print(f"   ✓ Duplicates removed: {len(raw)} rows → {len(dim)} rows")
    print(f"   ✓ product_code is unique")
    
    # Category normalization
    allowed_categories = {"Electronics", "Toys", "Bags", "Makeup", "Clothing", "Uncategorized"}
    assert set(dim["category"]).issubset(allowed_categories), f"Invalid categories: {set(dim['category']) - allowed_categories}"
    print(f"   ✓ Categories normalized: {set(dim['category'])}")
    print(f"      'GADGETS' → 'Electronics'")
    print(f"      'Toy' → 'Toys'")
    print(f"      'make up' → 'Makeup'")
    print(f"      'BAG' → 'Bags'")
    
    # Whitespace trimming
    assert not any(dim["product_name"].str.startswith(" ") | dim["product_name"].str.endswith(" ")), "Whitespace not trimmed"
    print(f"   ✓ Whitespace trimmed from product names")
    
    # Price conversion
    assert dim["price"].dtype.kind == "f", f"Price not numeric: {dim['price'].dtype}"
    print(f"   ✓ Price is numeric type: {dim['price'].dtype}")
    
    print("="*80 + "\n")
