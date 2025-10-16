import pandas as pd
from etl.transform.dim_user import transform_dim_user

# Mock raw user data to simulate extracted data
raw_data = {
    'id': [1, 2, 3],
    'username': ['isa', 'jm', 'lee'],
    'firstName': ['Isabella', 'John', 'Lee'],
    'lastName': ['Ross', 'Mendoza', 'Chan'],
    'gender': ['F', 'male', 'unknown'],
    'city': ['manila', 'QUEZON CITY', None],
    'country': ['philippines', 'PHILIPPINES', 'Japan'],
    'createdAt': ['2024-05-12', '05/13/2024', '10-07-2025']  # mixed formats
}

# Create DataFrame
df = pd.DataFrame(raw_data)

# Run ETL transformation
result = transform_dim_user(df)

# Display transformed data
print("\n=== Transformed User Dimension ===")
print(result)

# Check transformation validity
print("\n=== Validation Summary ===")
print(f"Rows before: {len(df)} | Rows after: {len(result)}")
print(f"Columns: {list(result.columns)}")

# Simple checks
assert 'user_key' in result.columns, "user_key column missing"
assert 'full_name' in result.columns, "full_name column missing"
assert not result['full_name'].isnull().any(), "Null full_name found"
assert len(df) == len(result), "Row count mismatch before and after transform"

print("\n✅ User dimension transformation test passed!")
