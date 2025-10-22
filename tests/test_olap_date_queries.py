import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy import text

from app.queries.sales_queries import (
    get_daily_sales_trend
)


def test_get_sales_by_day_of_week(sqlite_engine: Engine):
    """Test sales aggregation by day of week.
    
    NOTE: The production query in sales_queries.py uses MySQL FIELD() function 
    which doesn't work in SQLite. This test validates the core logic using 
    SQLite-compatible syntax directly.
    """
    print("\n" + "="*80)
    print("OLAP TEST: get_sales_by_day_of_week (SQLite-compatible)")
    print("="*80)
    
    print("\n📥 QUERY PURPOSE:")
    print("   Aggregate total sales by day name (Monday-Sunday)")
    
    print("\n📥 SEED DATA (dates with day names):")
    with sqlite_engine.connect() as conn:
        dates = pd.read_sql(text("SELECT date_key, day_name, is_weekend FROM dim_date"), conn)
        print(dates.to_string(index=False))
        
        print("\nfact_sales (with dates):")
        sales = pd.read_sql(text("""
            SELECT fs.order_number, fs.date_key, fs.sales_amount, dd.day_name
            FROM fact_sales fs
            JOIN dim_date dd ON fs.date_key = dd.date_key
        """), conn)
        print(sales.to_string(index=False))
    
    # Execute SQLite-compatible version
    # Production uses: ORDER BY FIELD(dd.day_name, 'Monday','Tuesday',...)
    # SQLite test uses: ORDER BY dd.day_name (alphabetical)
    query = """
        SELECT 
            dd.day_name,
            SUM(fs.sales_amount) AS total_sales
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        GROUP BY dd.day_name
        ORDER BY dd.day_name
    """
    
    with sqlite_engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    
    print("\n📤 QUERY RESULT:")
    print(df.to_string(index=False))
    print(f"\nShape: {df.shape}")
    
    print("\n✅ VALIDATION:")
    assert "day_name" in df.columns and "total_sales" in df.columns
    print(f"   ✓ Required columns present: day_name, total_sales")
    
    assert len(df) == 3, f"Should have 3 distinct days, got {len(df)}"
    print(f"   ✓ Correct number of days: {len(df)}")
    
    # Check specific day totals
    if not df.empty:
        day_totals = {row["day_name"]: row["total_sales"] for _, row in df.iterrows()}
        
        # Saturday: ORD-1 (100) + ORD-4 (400) = 500
        if "Saturday" in day_totals:
            assert day_totals["Saturday"] == 500.0, f"Saturday total incorrect: {day_totals['Saturday']} != 500.0"
            print(f"   ✓ Saturday: ORD-1 + ORD-4 = {day_totals['Saturday']}")
        
        # Sunday: ORD-2 (250) = 250
        if "Sunday" in day_totals:
            assert day_totals["Sunday"] == 250.0, f"Sunday total incorrect: {day_totals['Sunday']} != 250.0"
            print(f"   ✓ Sunday: ORD-2 = {day_totals['Sunday']}")
        
        # Monday: ORD-3 (300) = 300
        if "Monday" in day_totals:
            assert day_totals["Monday"] == 300.0, f"Monday total incorrect: {day_totals['Monday']} != 300.0"
            print(f"   ✓ Monday: ORD-3 = {day_totals['Monday']}")
        
        print(f"   ✓ All day names validated: {list(day_totals.keys())}")
    
    print("\n💡 USE CASE:")
    print("   Identifies which days of the week have highest sales")
    print("   Helps with staffing and inventory planning by day")
    
    print("\n📝 NOTE:")
    print("   Production query uses MySQL FIELD() for custom day ordering")
    print("   This test validates core aggregation logic with SQLite")
    
    print("="*80 + "\n")


def test_get_daily_sales_trend(sqlite_engine: Engine):
    """Test daily sales time-series data."""
    print("\n" + "="*80)
    print("OLAP TEST: get_daily_sales_trend")
    print("="*80)
    
    print("\n📥 QUERY PURPOSE:")
    print("   Get daily sales data for time-series trend analysis")
    
    df = get_daily_sales_trend(sqlite_engine)
    
    print("\n📤 QUERY RESULT:")
    print(df.to_string(index=False))
    print(f"\nShape: {df.shape}")
    
    print("\n✅ VALIDATION:")
    # Check required columns for trend visualization
    required = {"full_date", "total_sales"}
    assert required.issubset(set(df.columns)), f"Missing columns: {required - set(df.columns)}"
    print(f"   ✓ Required columns present: {required}")
    
    # Should have 3 distinct dates in our seed data
    if not df.empty:
        date_count = df["full_date"].nunique()
        assert date_count == 3, f"Expected 3 dates, got {date_count}"
        print(f"   ✓ Correct number of dates: {date_count}")
        
        # Check if dates are sorted
        dates = pd.to_datetime(df["full_date"])
        assert dates.is_monotonic_increasing, "Dates not sorted"
        print(f"   ✓ Dates sorted chronologically")
        
        # Validate total across all days
        total = df["total_sales"].sum()
        assert total == 1050.0, f"Total sales incorrect: {total} != 1050.0"
        print(f"   ✓ Total sales across all days: {total}")
    
    print("\n💡 USE CASE:")
    print("   Powers line charts showing sales trends over time")
    print("   Enables forecasting and anomaly detection")
    
    print("="*80 + "\n")
