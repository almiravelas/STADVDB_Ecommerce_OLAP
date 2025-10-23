"""
Tests for Roll-up OLAP Operations
Tests aggregation to higher levels of granularity
"""
import pytest
import pandas as pd
from sqlalchemy.engine import Engine

# Import rollup query functions
import sys
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.queries.rollup_queries import (
    rollup_sales_by_year,
    rollup_sales_by_quarter,
    rollup_sales_by_category,
    rollup_sales_by_region
)


class TestRollupOperations:
    """Test suite for roll-up OLAP operations"""
    
    def test_rollup_sales_by_year_structure(self, sqlite_engine: Engine):
        """Test that rolling up to year level returns correct structure"""
        df, duration, query, params = rollup_sales_by_year(sqlite_engine)
        
        print("\n" + "="*80)
        print("ROLLUP TEST: Sales by Year")
        print("="*80)
        print(f"\n📊 Results Shape: {df.shape}")
        print(f"⏱️  Query Duration: {duration:.4f}s")
        print(f"\n📋 Data Preview:")
        print(df.to_string(index=False))
        
        # Validate structure
        assert not df.empty, "Result should not be empty"
        assert 'year' in df.columns, "Should have 'year' column"
        assert 'total_orders' in df.columns, "Should have 'total_orders' column"
        assert 'total_sales' in df.columns, "Should have 'total_sales' column"
        assert 'total_quantity' in df.columns, "Should have 'total_quantity' column"
        assert 'avg_order_value' in df.columns, "Should have 'avg_order_value' column"
        
        # Validate data types
        assert df['year'].dtype in ['int64', 'int32'], "Year should be integer"
        assert df['total_sales'].dtype in ['float64', 'float32'], "Sales should be float"
        
        # Validate aggregation
        assert df['total_orders'].sum() > 0, "Should have orders"
        assert df['total_sales'].sum() > 0, "Should have sales"
        
        print("\n✅ All assertions passed!")
        
    def test_rollup_sales_by_year_aggregation(self, sqlite_engine: Engine):
        """Test that year-level aggregation produces correct values"""
        df, _, _, _ = rollup_sales_by_year(sqlite_engine)
        
        print("\n" + "="*80)
        print("ROLLUP TEST: Year Aggregation Validation")
        print("="*80)
        
        # Check that we have data for 2021
        year_2021 = df[df['year'] == 2021]
        assert not year_2021.empty, "Should have data for 2021"
        
        # Test known values from seed data
        # We have 3 distinct orders: ORD-1, ORD-2, ORD-3, ORD-4
        # ORD-1, ORD-2 (2 lines), ORD-4 are in 2021
        # ORD-3 is also in 2021
        expected_orders = 4  # All orders are in 2021
        actual_orders = year_2021['total_orders'].iloc[0]
        
        print(f"\n📈 2021 Statistics:")
        print(f"   Orders: {actual_orders} (expected: {expected_orders})")
        print(f"   Sales: ${year_2021['total_sales'].iloc[0]:.2f}")
        print(f"   Quantity: {year_2021['total_quantity'].iloc[0]}")
        
        assert actual_orders == expected_orders, f"Expected {expected_orders} orders, got {actual_orders}"
        
        print("\n✅ Aggregation validated!")
        
    def test_rollup_sales_by_quarter_structure(self, sqlite_engine: Engine):
        """Test that rolling up to quarter level returns correct structure"""
        df, duration, query, params = rollup_sales_by_quarter(sqlite_engine)
        
        print("\n" + "="*80)
        print("ROLLUP TEST: Sales by Quarter")
        print("="*80)
        print(f"\n📊 Results Shape: {df.shape}")
        print(f"⏱️  Query Duration: {duration:.4f}s")
        print(f"\n📋 Data Preview:")
        print(df.to_string(index=False))
        
        # Validate structure
        assert not df.empty, "Result should not be empty"
        assert 'year' in df.columns, "Should have 'year' column"
        assert 'quarter' in df.columns, "Should have 'quarter' column"
        assert 'total_sales' in df.columns, "Should have 'total_sales' column"
        
        # Validate quarter values
        assert df['quarter'].min() >= 1, "Quarter should be at least 1"
        assert df['quarter'].max() <= 4, "Quarter should be at most 4"
        
        print("\n✅ All assertions passed!")
        
    def test_rollup_sales_by_category_structure(self, sqlite_engine: Engine):
        """Test that rolling up to category level returns correct structure"""
        df, duration, query, params = rollup_sales_by_category(sqlite_engine)
        
        print("\n" + "="*80)
        print("ROLLUP TEST: Sales by Category")
        print("="*80)
        print(f"\n📊 Results Shape: {df.shape}")
        print(f"⏱️  Query Duration: {duration:.4f}s")
        print(f"\n📋 Data Preview:")
        print(df.to_string(index=False))
        
        # Validate structure
        assert not df.empty, "Result should not be empty"
        assert 'category' in df.columns, "Should have 'category' column"
        assert 'total_sales' in df.columns, "Should have 'total_sales' column"
        assert 'product_count' in df.columns, "Should have 'product_count' column"
        
        # Validate categories from seed data
        categories = set(df['category'].tolist())
        expected_categories = {'Electronics', 'Toys', 'Bags'}
        assert categories == expected_categories, f"Expected {expected_categories}, got {categories}"
        
        # Validate sorting (should be DESC by total_sales)
        assert df['total_sales'].tolist() == sorted(df['total_sales'].tolist(), reverse=True), \
            "Should be sorted by total_sales DESC"
        
        print(f"\n📦 Categories found: {categories}")
        print("\n✅ All assertions passed!")
        
    def test_rollup_sales_by_region_structure(self, sqlite_engine: Engine):
        """Test that rolling up to region/continent level returns correct structure"""
        df, duration, query, params = rollup_sales_by_region(sqlite_engine)
        
        print("\n" + "="*80)
        print("ROLLUP TEST: Sales by Region")
        print("="*80)
        print(f"\n📊 Results Shape: {df.shape}")
        print(f"⏱️  Query Duration: {duration:.4f}s")
        print(f"\n📋 Data Preview:")
        print(df.to_string(index=False))
        
        # Validate structure
        assert not df.empty, "Result should not be empty"
        assert 'continent' in df.columns, "Should have 'continent' column"
        assert 'total_sales' in df.columns, "Should have 'total_sales' column"
        
        # Validate continents from seed data
        continents = set(df['continent'].tolist())
        expected_continents = {'Asia', 'Europe'}
        assert continents == expected_continents, f"Expected {expected_continents}, got {continents}"
        
        print(f"\n🌍 Continents found: {continents}")
        print("\n✅ All assertions passed!")
        
    def test_rollup_null_engine_handling(self):
        """Test that rollup functions handle None engine gracefully"""
        # Clear cache before testing with None engine
        rollup_sales_by_year.clear()
        
        df, duration, query, params = rollup_sales_by_year(None)
        
        assert df.empty, "Should return empty DataFrame for None engine"
        assert duration == 0.0, "Duration should be 0.0 for None engine"
        assert query == "", "Query should be empty string for None engine"
        
        print("\n✅ Null engine handling validated!")
        
    def test_rollup_query_performance(self, sqlite_engine: Engine):
        """Test that rollup queries execute within reasonable time"""
        _, duration, _, _ = rollup_sales_by_year(sqlite_engine)
        
        print(f"\n⏱️  Query execution time: {duration:.4f}s")
        
        # For in-memory SQLite with small dataset, should be very fast
        assert duration < 1.0, f"Query took too long: {duration:.4f}s"
        
        print("✅ Performance test passed!")


class TestRollupBusinessLogic:
    """Test business logic and data correctness in rollup operations"""
    
    def test_rollup_distinct_order_counting(self, sqlite_engine: Engine):
        """Test that orders with multiple line items are counted only once"""
        # Clear cache to ensure fresh query
        rollup_sales_by_year.clear()
        
        df, _, _, _ = rollup_sales_by_year(sqlite_engine)
        
        # ORD-2 has 2 line items but should count as 1 order
        total_orders = df['total_orders'].sum()
        
        print(f"\n📊 Total distinct orders: {total_orders}")
        
        # We have 4 distinct orders (ORD-1, ORD-2, ORD-3, ORD-4)
        assert total_orders == 4, f"Expected 4 distinct orders, got {total_orders}"
        
        print("✅ Distinct order counting validated!")
        
    def test_rollup_avg_order_value_calculation(self, sqlite_engine: Engine):
        """Test that average order value is calculated correctly"""
        # Clear cache to ensure fresh query
        rollup_sales_by_year.clear()
        
        df, _, _, _ = rollup_sales_by_year(sqlite_engine)
        
        year_2021 = df[df['year'] == 2021]
        total_sales = year_2021['total_sales'].iloc[0]
        total_orders = year_2021['total_orders'].iloc[0]
        avg_order_value = year_2021['avg_order_value'].iloc[0]
        
        expected_aov = total_sales / total_orders
        
        print(f"\n💰 Average Order Value:")
        print(f"   Total Sales: ${total_sales:.2f}")
        print(f"   Total Orders: {total_orders}")
        print(f"   Calculated AOV: ${avg_order_value:.2f}")
        print(f"   Expected AOV: ${expected_aov:.2f}")
        
        # Allow small floating point difference
        assert abs(avg_order_value - expected_aov) < 0.01, \
            f"AOV mismatch: {avg_order_value} vs {expected_aov}"
        
        print("✅ AOV calculation validated!")
        
    def test_rollup_hierarchy_consistency(self, sqlite_engine: Engine):
        """Test that aggregations are consistent across hierarchy levels"""
        # Clear cache to ensure fresh queries
        rollup_sales_by_year.clear()
        rollup_sales_by_quarter.clear()
        
        # Get year and quarter level data
        year_df, _, _, _ = rollup_sales_by_year(sqlite_engine)
        quarter_df, _, _, _ = rollup_sales_by_quarter(sqlite_engine)
        
        # Sum of quarters should equal year total for 2021
        year_2021_sales = year_df[year_df['year'] == 2021]['total_sales'].iloc[0]
        quarters_2021_sales = quarter_df[quarter_df['year'] == 2021]['total_sales'].sum()
        
        print(f"\n📊 Hierarchy Consistency Check:")
        print(f"   Year 2021 Total: ${year_2021_sales:.2f}")
        print(f"   Sum of Quarters: ${quarters_2021_sales:.2f}")
        
        # Should be equal (allowing small floating point difference)
        assert abs(year_2021_sales - quarters_2021_sales) < 0.01, \
            f"Hierarchy inconsistency: {year_2021_sales} vs {quarters_2021_sales}"
        
        print("✅ Hierarchy consistency validated!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
