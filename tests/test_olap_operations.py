"""
Test OLAP Operations: Roll-up, Drill-down, Slice, Dice, Pivot
Tests the new OLAP query functions added to the dashboard
"""
import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy import text

from app.queries.olap_queries import (
    # Roll-up operations
    rollup_sales_by_year,
    rollup_sales_by_quarter,
    rollup_sales_by_category,
    rollup_sales_by_courier,
    
    # Drill-down operations
    drilldown_year_to_month,
    drilldown_category_to_product,
    drilldown_month_to_day,
    drilldown_courier_to_vehicle,
    
    # Slice operations
    slice_by_year,
    slice_by_category,
    slice_by_city,
    slice_by_courier,
    
    # Dice operations
    dice_multi_dimension,
    
    # Pivot operations
    pivot_category_by_month,
    pivot_city_by_category,
    pivot_year_by_quarter,
    
    # Helper functions
    get_available_years,
    get_available_categories,
    get_available_cities,
    get_available_couriers,
    get_available_vehicle_types
)


def test_rollup_sales_by_year(sqlite_engine: Engine):
    """Test roll-up to year level"""
    print("\n" + "="*80)
    print("OLAP TEST: Roll-up by Year")
    print("="*80)
    
    df, duration = rollup_sales_by_year(sqlite_engine)
    
    print("\n📤 QUERY RESULT:")
    print(df.to_string(index=False))
    print(f"\nShape: {df.shape}")
    print(f"Query time: {duration:.4f} seconds")
    
    print("\n✅ VALIDATION:")
    required_cols = {"year", "total_orders", "total_sales", "total_quantity", "avg_order_value"}
    assert required_cols.issubset(set(df.columns)), f"Missing columns: {required_cols - set(df.columns)}"
    print(f"   ✓ All required columns present")
    
    # Check that we have data
    assert len(df) > 0, "No data returned"
    print(f"   ✓ Years with data: {sorted(df['year'].tolist())}")
    
    # Check aggregations make sense
    assert df['total_sales'].sum() > 0, "Total sales should be > 0"
    assert df['total_orders'].sum() > 0, "Total orders should be > 0"
    print(f"   ✓ Total sales across all years: ₱{df['total_sales'].sum():,.2f}")
    
    print("="*80 + "\n")


def test_rollup_sales_by_quarter(sqlite_engine: Engine):
    """Test roll-up to quarter level"""
    print("\n" + "="*80)
    print("OLAP TEST: Roll-up by Quarter")
    print("="*80)
    
    df, duration = rollup_sales_by_quarter(sqlite_engine)
    
    print("\n📤 QUERY RESULT:")
    print(df.head(10).to_string(index=False))
    print(f"\nShape: {df.shape}")
    print(f"Query time: {duration:.4f} seconds")
    
    print("\n✅ VALIDATION:")
    required_cols = {"year", "quarter", "total_orders", "total_sales"}
    assert required_cols.issubset(set(df.columns)), f"Missing columns"
    print(f"   ✓ All required columns present")
    
    # Check quarters are valid (1-4)
    assert df['quarter'].min() >= 1 and df['quarter'].max() <= 4, "Invalid quarter values"
    print(f"   ✓ Valid quarters: {sorted(df['quarter'].unique())}")
    
    print("="*80 + "\n")


def test_rollup_sales_by_category(sqlite_engine: Engine):
    """Test roll-up to product category level"""
    print("\n" + "="*80)
    print("OLAP TEST: Roll-up by Category")
    print("="*80)
    
    df, duration = rollup_sales_by_category(sqlite_engine)
    
    print("\n📤 QUERY RESULT:")
    print(df.to_string(index=False))
    print(f"\nShape: {df.shape}")
    print(f"Query time: {duration:.4f} seconds")
    
    print("\n✅ VALIDATION:")
    assert "category" in df.columns and "total_sales" in df.columns
    print(f"   ✓ Required columns present")
    
    assert len(df) > 0, "No categories found"
    print(f"   ✓ Categories: {sorted(df['category'].tolist())}")
    
    print("="*80 + "\n")


def test_rollup_sales_by_courier(sqlite_engine: Engine):
    """Test roll-up to courier level"""
    print("\n" + "="*80)
    print("OLAP TEST: Roll-up by Courier")
    print("="*80)
    
    df, duration = rollup_sales_by_courier(sqlite_engine)
    
    print("\n📤 QUERY RESULT:")
    print(df.to_string(index=False))
    print(f"\nShape: {df.shape}")
    print(f"Query time: {duration:.4f} seconds")
    
    print("\n✅ VALIDATION:")
    required_cols = {"courier_name", "total_sales", "rider_count"}
    assert required_cols.issubset(set(df.columns)), f"Missing columns"
    print(f"   ✓ All required columns present")
    
    assert len(df) > 0, "No couriers found"
    print(f"   ✓ Couriers: {sorted(df['courier_name'].tolist())}")
    
    print("="*80 + "\n")


def test_drilldown_year_to_month(sqlite_engine: Engine):
    """Test drill-down from year to month"""
    print("\n" + "="*80)
    print("OLAP TEST: Drill-down Year → Month")
    print("="*80)
    
    # Get available years first
    years = get_available_years(sqlite_engine)
    print(f"\n📥 Available years: {years}")
    
    if not years:
        print("   ⚠️  No years available, skipping test")
        return
    
    # Test with first available year
    test_year = years[0]
    df, duration = drilldown_year_to_month(sqlite_engine, test_year)
    
    print(f"\n📤 QUERY RESULT for year {test_year}:")
    print(df.to_string(index=False))
    print(f"\nShape: {df.shape}")
    print(f"Query time: {duration:.4f} seconds")
    
    print("\n✅ VALIDATION:")
    assert "month_name" in df.columns and "total_sales" in df.columns
    print(f"   ✓ Months with data: {sorted(df['month_name'].unique())}")
    
    print("="*80 + "\n")


def test_drilldown_courier_to_vehicle(sqlite_engine: Engine):
    """Test drill-down from courier to vehicle type"""
    print("\n" + "="*80)
    print("OLAP TEST: Drill-down Courier → Vehicle Type")
    print("="*80)
    
    # Get available couriers first
    couriers = get_available_couriers(sqlite_engine)
    print(f"\n📥 Available couriers: {couriers}")
    
    if not couriers:
        print("   ⚠️  No couriers available, skipping test")
        return
    
    # Test with first available courier
    test_courier = couriers[0]
    df, duration = drilldown_courier_to_vehicle(sqlite_engine, test_courier)
    
    print(f"\n📤 QUERY RESULT for courier '{test_courier}':")
    print(df.to_string(index=False))
    print(f"\nShape: {df.shape}")
    print(f"Query time: {duration:.4f} seconds")
    
    print("\n✅ VALIDATION:")
    required_cols = {"vehicleType", "total_sales", "rider_count"}
    assert required_cols.issubset(set(df.columns)), f"Missing columns"
    print(f"   ✓ Vehicle types: {sorted(df['vehicleType'].tolist())}")
    
    print("="*80 + "\n")


def test_slice_by_year(sqlite_engine: Engine):
    """Test slice by year"""
    print("\n" + "="*80)
    print("OLAP TEST: Slice by Year")
    print("="*80)
    
    # Get available years
    years = get_available_years(sqlite_engine)
    print(f"\n📥 Available years (filtered): {years}")
    
    # Should only return 2024 and 2025
    assert set(years).issubset({2024, 2025}), f"Years should be filtered to 2024 and 2025 only, got {years}"
    print(f"   ✓ Year filter working correctly: {years}")
    
    if not years:
        print("   ⚠️  No years available, skipping test")
        return
    
    # Test with first available year
    test_year = years[0]
    df, duration = slice_by_year(sqlite_engine, test_year)
    
    print(f"\n📤 QUERY RESULT for year {test_year}:")
    print(df.head(10).to_string(index=False))
    print(f"\nShape: {df.shape}")
    print(f"Query time: {duration:.4f} seconds")
    
    print("\n✅ VALIDATION:")
    # All rows should be from the selected year
    assert (df['year'] == test_year).all(), f"Found data from other years"
    print(f"   ✓ All data is from year {test_year}")
    
    print("="*80 + "\n")


def test_slice_by_courier(sqlite_engine: Engine):
    """Test slice by courier"""
    print("\n" + "="*80)
    print("OLAP TEST: Slice by Courier")
    print("="*80)
    
    # Get available couriers
    couriers = get_available_couriers(sqlite_engine)
    print(f"\n📥 Available couriers: {couriers}")
    
    if not couriers:
        print("   ⚠️  No couriers available, skipping test")
        return
    
    # Test with first available courier
    test_courier = couriers[0]
    df, duration = slice_by_courier(sqlite_engine, test_courier)
    
    print(f"\n📤 QUERY RESULT for courier '{test_courier}':")
    print(df.head(10).to_string(index=False))
    print(f"\nShape: {df.shape}")
    print(f"Query time: {duration:.4f} seconds")
    
    print("\n✅ VALIDATION:")
    # All rows should be from the selected courier
    assert (df['courier_name'] == test_courier).all(), f"Found data from other couriers"
    print(f"   ✓ All data is from courier '{test_courier}'")
    
    # Should have multi-dimensional data
    assert "vehicleType" in df.columns, "Missing vehicle type"
    assert "category" in df.columns, "Missing category"
    print(f"   ✓ Multi-dimensional data present")
    
    print("="*80 + "\n")


def test_dice_multi_dimension(sqlite_engine: Engine):
    """Test dice operation with multiple dimensions"""
    print("\n" + "="*80)
    print("OLAP TEST: Dice (Multi-dimensional filtering)")
    print("="*80)
    
    # Get available values
    years = get_available_years(sqlite_engine)
    categories = get_available_categories(sqlite_engine)
    cities = get_available_cities(sqlite_engine)
    couriers = get_available_couriers(sqlite_engine)
    
    print(f"\n📥 Available dimension values:")
    print(f"   Years: {years[:3]}..." if len(years) > 3 else f"   Years: {years}")
    print(f"   Categories: {categories[:3]}..." if len(categories) > 3 else f"   Categories: {categories}")
    print(f"   Cities: {cities[:3]}..." if len(cities) > 3 else f"   Cities: {cities}")
    print(f"   Couriers: {couriers[:2]}..." if len(couriers) > 2 else f"   Couriers: {couriers}")
    
    if not years or not categories or not cities or not couriers:
        print("   ⚠️  Missing dimension data, skipping test")
        return
    
    # Test with filtered dimensions
    test_years = years[:1] if years else []
    test_categories = categories[:2] if len(categories) >= 2 else categories
    test_cities = cities[:2] if len(cities) >= 2 else cities
    test_couriers = couriers[:1] if couriers else []
    
    print(f"\n🎲 Dice filters:")
    print(f"   Years IN {test_years}")
    print(f"   Categories IN {test_categories}")
    print(f"   Cities IN {test_cities}")
    print(f"   Couriers IN {test_couriers}")
    
    df, duration = dice_multi_dimension(
        sqlite_engine, 
        test_years, 
        test_categories, 
        test_cities, 
        test_couriers
    )
    
    print(f"\n📤 QUERY RESULT:")
    print(df.head(20).to_string(index=False))
    print(f"\nShape: {df.shape}")
    print(f"Query time: {duration:.4f} seconds")
    
    print("\n✅ VALIDATION:")
    # Check all filters are applied
    if test_years:
        assert df['year'].isin(test_years).all(), "Year filter not applied"
        print(f"   ✓ Year filter applied")
    
    if test_categories:
        assert df['category'].isin(test_categories).all(), "Category filter not applied"
        print(f"   ✓ Category filter applied")
    
    if test_cities:
        assert df['user_city'].isin(test_cities).all(), "City filter not applied"
        print(f"   ✓ City filter applied")
    
    if test_couriers:
        assert df['courier_name'].isin(test_couriers).all(), "Courier filter not applied"
        print(f"   ✓ Courier filter applied")
    
    # Check we have rider dimension data
    assert "courier_name" in df.columns and "vehicleType" in df.columns
    print(f"   ✓ Rider dimension included")
    
    print("="*80 + "\n")


def test_pivot_category_by_month(sqlite_engine: Engine):
    """Test pivot: categories × months"""
    print("\n" + "="*80)
    print("OLAP TEST: Pivot Category × Month")
    print("="*80)
    
    df, duration = pivot_category_by_month(sqlite_engine)
    
    print("\n📤 QUERY RESULT:")
    print(df.head(20).to_string(index=False))
    print(f"\nShape: {df.shape}")
    print(f"Query time: {duration:.4f} seconds")
    
    print("\n✅ VALIDATION:")
    required_cols = {"category", "month_name", "total_sales"}
    assert required_cols.issubset(set(df.columns)), f"Missing columns"
    print(f"   ✓ Pivot dimensions present: category, month_name")
    
    print("="*80 + "\n")


def test_helper_functions(sqlite_engine: Engine):
    """Test helper functions for getting available values"""
    print("\n" + "="*80)
    print("OLAP TEST: Helper Functions")
    print("="*80)
    
    print("\n📥 Testing dimension value retrieval:")
    
    years = get_available_years(sqlite_engine)
    print(f"   Years (should be 2024, 2025 only): {years}")
    assert set(years).issubset({2024, 2025}), f"Year filter not working: {years}"
    print(f"   ✓ Year filter working correctly")
    
    categories = get_available_categories(sqlite_engine)
    print(f"   Categories: {categories[:5]}..." if len(categories) > 5 else f"   Categories: {categories}")
    assert len(categories) > 0, "No categories found"
    print(f"   ✓ Found {len(categories)} categories")
    
    cities = get_available_cities(sqlite_engine)
    print(f"   Cities: {cities[:5]}..." if len(cities) > 5 else f"   Cities: {cities}")
    assert len(cities) > 0, "No cities found"
    print(f"   ✓ Found {len(cities)} cities")
    
    couriers = get_available_couriers(sqlite_engine)
    print(f"   Couriers: {couriers}")
    assert len(couriers) > 0, "No couriers found"
    print(f"   ✓ Found {len(couriers)} couriers")
    
    vehicle_types = get_available_vehicle_types(sqlite_engine)
    print(f"   Vehicle Types: {vehicle_types}")
    assert len(vehicle_types) > 0, "No vehicle types found"
    print(f"   ✓ Found {len(vehicle_types)} vehicle types")
    
    print("="*80 + "\n")
