"""
Tests for Pivot OLAP Operations
Tests cross-tabulation and data reorganization
"""
import pytest
import pandas as pd
from sqlalchemy.engine import Engine

# Import pivot query functions
import sys
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.queries.pivot_queries import (
    pivot_category_by_month,
    pivot_city_by_category,
    pivot_year_by_quarter
)


class TestPivotOperations:
    """Test suite for pivot OLAP operations"""
    
    def test_pivot_category_by_month_structure(self, sqlite_engine: Engine):
        """Test pivoting categories by months"""
        df, duration = pivot_category_by_month(sqlite_engine)
        
        print("\n" + "="*80)
        print("PIVOT TEST: Category by Month")
        print("="*80)
        print(f"\n📊 Results Shape: {df.shape}")
        print(f"⏱️  Query Duration: {duration:.4f}s")
        print(f"\n📋 Data Preview:")
        print(df.to_string(index=False))
        
        # Validate structure
        assert not df.empty, "Result should not be empty"
        assert 'category' in df.columns, "Should have 'category' column"
        assert 'year' in df.columns, "Should have 'year' column"
        assert 'month' in df.columns, "Should have 'month' column"
        assert 'month_name' in df.columns, "Should have 'month_name' column"
        assert 'total_sales' in df.columns, "Should have 'total_sales' column"
        
        # Validate data types
        assert df['month'].dtype in ['int64', 'int32'], "Month should be integer"
        assert df['total_sales'].dtype in ['float64', 'float32'], "Sales should be float"
        
        # Validate categories exist
        categories = df['category'].unique()
        assert len(categories) > 0, "Should have categories"
        
        print(f"\n📦 Categories: {list(categories)}")
        print(f"📅 Months: {sorted(df['month'].unique())}")
        print("\n✅ All assertions passed!")
        
    def test_pivot_category_by_month_pivot_transformation(self, sqlite_engine: Engine):
        """Test that data can be pivoted into matrix form"""
        df, _ = pivot_category_by_month(sqlite_engine)
        
        print("\n" + "="*80)
        print("PIVOT TEST: Matrix Transformation")
        print("="*80)
        
        # Pivot the data
        pivoted = df.pivot_table(
            index='category',
            columns='month_name',
            values='total_sales',
            aggfunc='sum',
            fill_value=0
        )
        
        print(f"\n📊 Pivoted Shape: {pivoted.shape}")
        print(f"\n📋 Pivoted Data:")
        print(pivoted.to_string())
        
        # Validate pivot
        assert not pivoted.empty, "Pivoted table should not be empty"
        assert len(pivoted.index) > 0, "Should have category rows"
        assert len(pivoted.columns) > 0, "Should have month columns"
        
        print("\n✅ Matrix transformation validated!")
        
    def test_pivot_city_by_category_structure(self, sqlite_engine: Engine):
        """Test pivoting cities by categories"""
        df, duration = pivot_city_by_category(sqlite_engine)
        
        print("\n" + "="*80)
        print("PIVOT TEST: City by Category")
        print("="*80)
        print(f"\n📊 Results Shape: {df.shape}")
        print(f"⏱️  Query Duration: {duration:.4f}s")
        print(f"\n📋 Data Preview:")
        print(df.to_string(index=False))
        
        # Validate structure
        assert not df.empty, "Result should not be empty"
        assert 'city' in df.columns, "Should have 'city' column"
        assert 'category' in df.columns, "Should have 'category' column"
        assert 'total_sales' in df.columns, "Should have 'total_sales' column"
        assert 'total_orders' in df.columns, "Should have 'total_orders' column"
        
        # Validate cities from seed data
        cities = df['city'].unique()
        expected_cities = {'Manila', 'Tokyo', 'Berlin'}
        assert set(cities) == expected_cities, f"Expected {expected_cities}, got {set(cities)}"
        
        print(f"\n🏙️  Cities: {list(cities)}")
        print(f"📦 Categories: {list(df['category'].unique())}")
        print("\n✅ All assertions passed!")
        
    def test_pivot_city_by_category_matrix(self, sqlite_engine: Engine):
        """Test city-category pivot matrix"""
        df, _ = pivot_city_by_category(sqlite_engine)
        
        print("\n" + "="*80)
        print("PIVOT TEST: City-Category Matrix")
        print("="*80)
        
        # Create pivot table
        sales_pivot = df.pivot_table(
            index='city',
            columns='category',
            values='total_sales',
            aggfunc='sum',
            fill_value=0
        )
        
        orders_pivot = df.pivot_table(
            index='city',
            columns='category',
            values='total_orders',
            aggfunc='sum',
            fill_value=0
        )
        
        print(f"\n💰 Sales by City and Category:")
        print(sales_pivot.to_string())
        
        print(f"\n📦 Orders by City and Category:")
        print(orders_pivot.to_string())
        
        # Validate
        assert not sales_pivot.empty, "Sales pivot should not be empty"
        assert not orders_pivot.empty, "Orders pivot should not be empty"
        
        # All values should be non-negative
        assert (sales_pivot >= 0).all().all(), "All sales should be non-negative"
        assert (orders_pivot >= 0).all().all(), "All orders should be non-negative"
        
        print("\n✅ City-Category matrix validated!")
        
    def test_pivot_year_by_quarter_structure(self, sqlite_engine: Engine):
        """Test pivoting years by quarters"""
        df, duration = pivot_year_by_quarter(sqlite_engine)
        
        print("\n" + "="*80)
        print("PIVOT TEST: Year by Quarter")
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
        assert 'total_orders' in df.columns, "Should have 'total_orders' column"
        
        # Validate quarter values
        assert df['quarter'].min() >= 1, "Quarter should be at least 1"
        assert df['quarter'].max() <= 4, "Quarter should be at most 4"
        
        print(f"\n📅 Years: {sorted(df['year'].unique())}")
        print(f"📅 Quarters: {sorted(df['quarter'].unique())}")
        print("\n✅ All assertions passed!")
        
    def test_pivot_year_by_quarter_matrix(self, sqlite_engine: Engine):
        """Test year-quarter pivot matrix"""
        df, _ = pivot_year_by_quarter(sqlite_engine)
        
        print("\n" + "="*80)
        print("PIVOT TEST: Year-Quarter Matrix")
        print("="*80)
        
        # Create pivot table
        pivot = df.pivot_table(
            index='year',
            columns='quarter',
            values='total_sales',
            aggfunc='sum',
            fill_value=0
        )
        
        print(f"\n💰 Sales by Year and Quarter:")
        print(pivot.to_string())
        
        # Validate
        assert not pivot.empty, "Pivot should not be empty"
        
        # Calculate quarterly growth if multiple years
        if len(pivot.index) > 1:
            print("\n📈 Year-over-Year Analysis:")
            for col in pivot.columns:
                if pivot[col].sum() > 0:
                    print(f"   Q{col}: ${pivot[col].sum():.2f}")
        
        print("\n✅ Year-Quarter matrix validated!")
        
    def test_pivot_null_engine_handling(self):
        """Test that pivot functions handle None engine gracefully"""
        # Clear cache before testing with None engine
        pivot_category_by_month.clear()
        
        df, duration = pivot_category_by_month(None)
        
        assert df.empty, "Should return empty DataFrame for None engine"
        assert duration == 0.0, "Duration should be 0.0 for None engine"
        
        print("\n✅ Null engine handling validated!")


class TestPivotBusinessLogic:
    """Test business logic and analytical capabilities of pivot operations"""
    
    def test_pivot_cross_dimensional_analysis(self, sqlite_engine: Engine):
        """Test that pivot enables cross-dimensional analysis"""
        df, _ = pivot_city_by_category(sqlite_engine)
        
        print("\n" + "="*80)
        print("PIVOT TEST: Cross-Dimensional Analysis")
        print("="*80)
        
        # Analyze which city buys which category most
        pivot = df.pivot_table(
            index='city',
            columns='category',
            values='total_sales',
            aggfunc='sum',
            fill_value=0
        )
        
        print(f"\n📊 City-Category Sales Matrix:")
        print(pivot.to_string())
        
        # Find top category per city
        print(f"\n🏆 Top Category per City:")
        for city in pivot.index:
            top_category = pivot.loc[city].idxmax()
            top_sales = pivot.loc[city].max()
            print(f"   {city}: {top_category} (${top_sales:.2f})")
        
        print("\n✅ Cross-dimensional analysis validated!")
        
    def test_pivot_trend_analysis(self, sqlite_engine: Engine):
        """Test pivot for trend analysis"""
        df, _ = pivot_category_by_month(sqlite_engine)
        
        print("\n" + "="*80)
        print("PIVOT TEST: Trend Analysis")
        print("="*80)
        
        # Focus on one year
        df_2021 = df[df['year'] == 2021]
        
        if not df_2021.empty:
            # Pivot by month
            pivot = df_2021.pivot_table(
                index='category',
                columns='month',
                values='total_sales',
                aggfunc='sum',
                fill_value=0
            )
            
            print(f"\n📈 2021 Monthly Trends by Category:")
            print(pivot.to_string())
            
            # Identify trending categories
            print(f"\n📊 Category Performance:")
            for category in pivot.index:
                total = pivot.loc[category].sum()
                months_with_sales = (pivot.loc[category] > 0).sum()
                print(f"   {category}: ${total:.2f} across {months_with_sales} months")
            
            print("\n✅ Trend analysis validated!")
        
    def test_pivot_data_density(self, sqlite_engine: Engine):
        """Test pivot data density and sparsity"""
        df, _ = pivot_city_by_category(sqlite_engine)
        
        print("\n" + "="*80)
        print("PIVOT TEST: Data Density")
        print("="*80)
        
        # Create full cartesian product
        cities = df['city'].unique()
        categories = df['category'].unique()
        max_combinations = len(cities) * len(categories)
        actual_combinations = len(df)
        
        density = (actual_combinations / max_combinations) * 100
        
        print(f"\n📊 Data Density:")
        print(f"   Cities: {len(cities)}")
        print(f"   Categories: {len(categories)}")
        print(f"   Possible Combinations: {max_combinations}")
        print(f"   Actual Combinations: {actual_combinations}")
        print(f"   Density: {density:.1f}%")
        
        # Should have some data
        assert actual_combinations > 0, "Should have some combinations"
        
        print("\n✅ Data density validated!")
        
    def test_pivot_aggregation_consistency(self, sqlite_engine: Engine):
        """Test that pivot maintains aggregation consistency"""
        df, _ = pivot_city_by_category(sqlite_engine)
        
        print("\n" + "="*80)
        print("PIVOT TEST: Aggregation Consistency")
        print("="*80)
        
        # Total sales
        total_sales = df['total_sales'].sum()
        total_orders = df['total_orders'].sum()
        
        print(f"\n💰 Grand Totals:")
        print(f"   Total Sales: ${total_sales:.2f}")
        print(f"   Total Orders: {total_orders}")
        
        # Compare with rollup
        from app.queries.rollup_queries import rollup_sales_by_year
        rollup_df, _, _, _ = rollup_sales_by_year(sqlite_engine)
        rollup_total = rollup_df['total_sales'].sum()
        
        print(f"\n🔄 Validation:")
        print(f"   Pivot Total: ${total_sales:.2f}")
        print(f"   Rollup Total: ${rollup_total:.2f}")
        
        # Should match (allowing small floating point difference)
        assert abs(total_sales - rollup_total) < 0.01, \
            f"Aggregation mismatch: {total_sales} vs {rollup_total}"
        
        print("\n✅ Aggregation consistency validated!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
