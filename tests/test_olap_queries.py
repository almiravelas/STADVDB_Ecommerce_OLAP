import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy import text

from app.queries.rider_queries import get_sales_for_dashboard
from app.queries.product_queries import get_dashboard_product_data
from app.queries.sales_queries import (
    get_sales_per_month,
    get_sales_per_year,
    get_sales_weekend_vs_weekday
)


def test_get_sales_for_dashboard_rider(sqlite_engine: Engine):
    """Test rider dashboard query - aggregated by order."""
    print("\n" + "="*80)
    print("OLAP TEST: get_sales_for_dashboard (Rider Analytics)")
    print("="*80)
    
    print("\n📥 SEED DATA:")
    with sqlite_engine.connect() as conn:
        print("\ndim_rider:")
        riders = pd.read_sql(text("SELECT * FROM dim_rider"), conn)
        print(riders.to_string(index=False))
        
        print("\nfact_sales (relevant columns):")
        sales = pd.read_sql(text("SELECT order_number, rider_key, sales_amount FROM fact_sales"), conn)
        print(sales.to_string(index=False))
    
    df, duration = get_sales_for_dashboard(sqlite_engine)
    
    print("\n📤 QUERY RESULT (aggregated by order):")
    print(df.to_string(index=False))
    print(f"\nShape: {df.shape}")
    print(f"Query time: {duration:.4f} seconds")
    
    print("\n✅ VALIDATION:")
    # Should have one row per unique order
    expected_orders = {'ORD-1', 'ORD-2', 'ORD-3', 'ORD-4'}
    assert set(df["order_number"]) == expected_orders, f"Expected orders {expected_orders}, got {set(df['order_number'])}"
    print(f"   ✓ All orders present: {sorted(df['order_number'].unique())}")
    
    # ORD-2 has 2 line items (200 + 50 = 250), should be aggregated
    ord2 = df[df["order_number"] == "ORD-2"].iloc[0]
    assert ord2["sales_amount"] == 250.0, f"ORD-2 not aggregated correctly: {ord2['sales_amount']} != 250.0"
    print(f"   ✓ ORD-2 aggregated: 200 + 50 = {ord2['sales_amount']}")
    
    # Check rider attribution
    assert ord2["rider_key"] == 101, f"ORD-2 rider incorrect: {ord2['rider_key']} != 101"
    assert ord2["rider_name"] == "Jane Smith", f"ORD-2 rider name incorrect"
    print(f"   ✓ ORD-2 rider: {ord2['rider_name']} (rider_key={ord2['rider_key']})")
    
    # Check date dimension join
    assert "year" in df.columns and "month_name" in df.columns
    print(f"   ✓ Date attributes present: year, month_name")
    
    print("="*80 + "\n")


def test_get_dashboard_product_data(sqlite_engine: Engine):
    """Test product dashboard query - aggregated by product and date."""
    print("\n" + "="*80)
    print("OLAP TEST: get_dashboard_product_data")
    print("="*80)
    
    print("\n📥 SEED DATA:")
    with sqlite_engine.connect() as conn:
        print("\ndim_product:")
        products = pd.read_sql(text("SELECT product_key, product_name, category, price FROM dim_product"), conn)
        print(products.to_string(index=False))
        
        print("\nfact_sales (relevant columns):")
        sales = pd.read_sql(text("SELECT order_number, product_key, sales_amount FROM fact_sales"), conn)
        print(sales.to_string(index=False))
    
    df, duration = get_dashboard_product_data(sqlite_engine)
    
    print("\n📤 QUERY RESULT (aggregated by product and date):")
    print(df.to_string(index=False))
    print(f"\nShape: {df.shape}")
    print(f"Query time: {duration:.4f} seconds")
    
    print("\n✅ VALIDATION:")
    # Should have product attributes
    assert "product_name" in df.columns and "category" in df.columns
    print(f"   ✓ Product attributes present: product_name, category")
    
    # Should have date attributes
    assert "year" in df.columns and "month_name" in df.columns
    print(f"   ✓ Date attributes present: year, month_name")
    
    # Check sales aggregation
    assert "total_sales" in df.columns
    print(f"   ✓ Sales aggregated as total_sales")
    
    # Laptop appears in 2 orders (ORD-1: 100, ORD-3: 300)
    laptop_sales = df[df["product_name"] == "Laptop"]["total_sales"].sum()
    assert laptop_sales == 400.0, f"Laptop total sales incorrect: {laptop_sales} != 400.0"
    print(f"   ✓ Laptop total: ORD-1 (100) + ORD-3 (300) = {laptop_sales}")
    
    # Check categories
    categories = set(df["category"])
    assert categories.issubset({"Electronics", "Toys", "Bags"}), f"Unexpected categories: {categories}"
    print(f"   ✓ Categories present: {categories}")
    
    print("="*80 + "\n")


def test_get_sales_per_month(sqlite_engine: Engine):
    """Test monthly sales aggregation."""
    print("\n" + "="*80)
    print("OLAP TEST: get_sales_per_month")
    print("="*80)
    
    print("\n📥 QUERY PURPOSE:")
    print("   Aggregate total sales by year and month")
    
    df = get_sales_per_month(sqlite_engine)
    
    print("\n📤 QUERY RESULT:")
    print(df.to_string(index=False))
    print(f"\nShape: {df.shape}")
    
    print("\n✅ VALIDATION:")
    required = {"year", "month", "month_name", "total_sales"}
    assert required.issubset(set(df.columns)), f"Missing columns: {required - set(df.columns)}"
    print(f"   ✓ All required columns present: {required}")
    
    # January 2021 has ORD-1 (100) + ORD-2 (250) + ORD-4 (400) = 750
    jan_2021 = df[(df["year"] == 2021) & (df["month"] == 1)]
    if not jan_2021.empty:
        jan_sales = jan_2021.iloc[0]["total_sales"]
        assert jan_sales == 750.0, f"January 2021 sales incorrect: {jan_sales} != 750.0"
        print(f"   ✓ January 2021: ORD-1 (100) + ORD-2 (250) + ORD-4 (400) = {jan_sales}")
    
    # May 2021 has ORD-3 (300) = 300
    may_2021 = df[(df["year"] == 2021) & (df["month"] == 5)]
    if not may_2021.empty:
        may_sales = may_2021.iloc[0]["total_sales"]
        assert may_sales == 300.0, f"May 2021 sales incorrect: {may_sales} != 300.0"
        print(f"   ✓ May 2021: ORD-3 (300) = {may_sales}")
    
    print("="*80 + "\n")


def test_get_sales_per_year(sqlite_engine: Engine):
    """Test yearly sales aggregation."""
    print("\n" + "="*80)
    print("OLAP TEST: get_sales_per_year")
    print("="*80)
    
    print("\n📥 QUERY PURPOSE:")
    print("   Aggregate total sales by year")
    
    df = get_sales_per_year(sqlite_engine)
    
    print("\n📤 QUERY RESULT:")
    print(df.to_string(index=False))
    print(f"\nShape: {df.shape}")
    
    print("\n✅ VALIDATION:")
    assert "year" in df.columns and "total_sales" in df.columns
    print(f"   ✓ Required columns present: year, total_sales")
    
    # 2021 should have all orders: 100 + 250 + 300 + 400 = 1050
    sales_2021 = df[df["year"] == 2021]["total_sales"].iloc[0]
    assert sales_2021 == 1050.0, f"2021 total sales incorrect: {sales_2021} != 1050.0"
    print(f"   ✓ 2021 total: 100 + 250 + 300 + 400 = {sales_2021}")
    
    print("="*80 + "\n")


def test_get_sales_weekend_vs_weekday(sqlite_engine: Engine):
    """Test weekend vs weekday sales comparison."""
    print("\n" + "="*80)
    print("OLAP TEST: get_sales_weekend_vs_weekday")
    print("="*80)
    
    print("\n📥 QUERY PURPOSE:")
    print("   Compare total sales on weekends vs weekdays")
    
    print("\n📥 SEED DATA (dates):")
    with sqlite_engine.connect() as conn:
        dates = pd.read_sql(text("SELECT date_key, day_name, is_weekend FROM dim_date"), conn)
        print(dates.to_string(index=False))
    
    df = get_sales_weekend_vs_weekday(sqlite_engine)
    
    print("\n📤 QUERY RESULT:")
    print(df.to_string(index=False))
    print(f"\nShape: {df.shape}")
    
    print("\n✅ VALIDATION:")
    assert "is_weekend" in df.columns and "total_sales" in df.columns
    print(f"   ✓ Required columns present: is_weekend, total_sales")
    
    # Weekend (Saturday, Sunday): ORD-1 (100) + ORD-2 (250) + ORD-4 (400) = 750
    weekend = df[df["is_weekend"] == "Y"]
    if not weekend.empty:
        weekend_sales = weekend.iloc[0]["total_sales"]
        assert weekend_sales == 750.0, f"Weekend sales incorrect: {weekend_sales} != 750.0"
        print(f"   ✓ Weekend (Sat+Sun): ORD-1 + ORD-2 + ORD-4 = {weekend_sales}")
    
    # Weekday (Monday): ORD-3 (300) = 300
    weekday = df[df["is_weekend"] == "N"]
    if not weekday.empty:
        weekday_sales = weekday.iloc[0]["total_sales"]
        assert weekday_sales == 300.0, f"Weekday sales incorrect: {weekday_sales} != 300.0"
        print(f"   ✓ Weekday (Mon): ORD-3 = {weekday_sales}")
    
    print("\n💡 INSIGHT:")
    if not weekend.empty and not weekday.empty:
        print(f"   Weekend sales ({weekend_sales}) vs Weekday sales ({weekday_sales})")
        print(f"   Weekend represents {weekend_sales / (weekend_sales + weekday_sales) * 100:.1f}% of total")
    
    print("="*80 + "\n")
