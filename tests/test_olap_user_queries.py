import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy import text

from app.queries.user_queries import (
    get_user_data,
    get_distinct_user_attributes,
)


def test_get_user_data_no_filters(sqlite_engine: Engine):
    """Test OLAP query without filters - show aggregation results."""
    print("\n" + "="*80)
    print("OLAP TEST: get_user_data (no filters)")
    print("="*80)
    
    # Show seed data
    print("\n📥 SEED DATA:")
    with sqlite_engine.connect() as conn:
        print("\ndim_user:")
        users = pd.read_sql(text("SELECT * FROM dim_user"), conn)
        print(users.to_string(index=False))
        
        print("\nfact_sales:")
        sales = pd.read_sql(text("SELECT * FROM fact_sales"), conn)
        print(sales.to_string(index=False))
    
    df = get_user_data(sqlite_engine)
    
    print("\n📤 QUERY RESULT (aggregated by user_key):")
    print(df.to_string(index=False))
    print(f"\nShape: {df.shape}")
    
    print("\n✅ VALIDATION:")
    # Expect one row per user_key present in both tables (1..3)
    assert set(df["user_key"]) == {1, 2, 3}, f"Expected users 1,2,3 but got {set(df['user_key'])}"
    print(f"   ✓ All users present: {sorted(df['user_key'])}")
    
    # Validate aggregation for user 1:
    # sales_amount: 100 + 200 + 50 = 350; DISTINCT orders: {'ORD-1','ORD-2'} = 2
    row1 = df[df["user_key"] == 1].iloc[0]
    assert row1["sales_amount"] == 350.0, f"User 1 sales_amount incorrect: {row1['sales_amount']} != 350.0"
    assert row1["total_orders"] == 2, f"User 1 total_orders incorrect: {row1['total_orders']} != 2"
    print(f"   ✓ User 1: sales_amount = 100 + 200 + 50 = {row1['sales_amount']}")
    print(f"            total_orders = DISTINCT(ORD-1, ORD-2) = {row1['total_orders']}")
    
    row2 = df[df["user_key"] == 2].iloc[0]
    assert row2["sales_amount"] == 300.0
    assert row2["total_orders"] == 1
    print(f"   ✓ User 2: sales_amount = {row2['sales_amount']}, total_orders = {row2['total_orders']}")
    
    row3 = df[df["user_key"] == 3].iloc[0]
    assert row3["sales_amount"] == 400.0
    assert row3["total_orders"] == 1
    print(f"   ✓ User 3: sales_amount = {row3['sales_amount']}, total_orders = {row3['total_orders']}")
    
    print("="*80 + "\n")


def test_get_user_data_with_filters(sqlite_engine: Engine):
    """Test OLAP query with demographic filters."""
    print("\n" + "="*80)
    print("OLAP TEST: get_user_data (with filters: Asia + Female)")
    print("="*80)
    
    print("\n📥 FILTER CRITERIA:")
    print("   continents = ['Asia']")
    print("   genders = ['Female']")
    
    # Filter by continent and gender
    df = get_user_data(sqlite_engine, continents=["Asia"], genders=["Female"])
    
    print("\n📤 QUERY RESULT (filtered):")
    if df.empty:
        print("   (empty result)")
    else:
        print(df.to_string(index=False))
    print(f"\nShape: {df.shape}")
    
    print("\n✅ VALIDATION:")
    # Only user_key 2 matches (Asia, Female)
    assert set(df["user_key"]) == {2}, f"Expected only user 2 but got {set(df['user_key'])}"
    print(f"   ✓ Only user 2 matches (Asia, Japan, Female)")
    
    assert df.iloc[0]["sales_amount"] == 300.0, f"User 2 sales_amount incorrect: {df.iloc[0]['sales_amount']}"
    assert df.iloc[0]["total_orders"] == 1, f"User 2 total_orders incorrect: {df.iloc[0]['total_orders']}"
    print(f"   ✓ User 2: sales_amount = {df.iloc[0]['sales_amount']}, total_orders = {df.iloc[0]['total_orders']}")
    
    print("\n💡 EXPLANATION:")
    print("   User 1: Asia, Philippines, Male → excluded by gender filter")
    print("   User 2: Asia, Japan, Female → ✓ matches all filters")
    print("   User 3: Europe, Germany, Female → excluded by continent filter")
    
    print("="*80 + "\n")


def test_get_distinct_user_attributes(sqlite_engine: Engine):
    """Test OLAP query for distinct filter options."""
    print("\n" + "="*80)
    print("OLAP TEST: get_distinct_user_attributes")
    print("="*80)
    
    print("\n📥 QUERY PURPOSE:")
    print("   Extract distinct values for UI filter dropdowns")
    
    attrs = get_distinct_user_attributes(sqlite_engine)
    
    print("\n📤 QUERY RESULT (distinct attributes):")
    print(f"   Continents: {attrs['continents']}")
    print(f"   Countries:  {attrs['countries']}")
    print(f"   Cities:     {attrs['cities']}")
    print(f"   Genders:    {attrs['genders']}")
    
    print("\n✅ VALIDATION:")
    assert "Asia" in attrs["continents"], "Asia missing from continents"
    assert "Europe" in attrs["continents"], "Europe missing from continents"
    print(f"   ✓ Continents contain Asia and Europe")
    
    assert "Philippines" in attrs["countries"], "Philippines missing"
    assert "Japan" in attrs["countries"], "Japan missing"
    assert "Germany" in attrs["countries"], "Germany missing"
    print(f"   ✓ All seeded countries present")
    
    assert {"Male", "Female"}.issubset(set(attrs["genders"])), "Male or Female missing"
    print(f"   ✓ Both genders present")
    
    print("\n💡 USE CASE:")
    print("   These lists populate the filter dropdowns in the Streamlit UI,")
    print("   allowing users to slice the data by demographics.")
    
    print("="*80 + "\n")
