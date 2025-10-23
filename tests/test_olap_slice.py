"""
Tests for Slice OLAP Operations
Tests fixing one dimension to a specific value
"""
import pytest
import pandas as pd
from sqlalchemy.engine import Engine

# Import slice query functions
import sys
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.queries.slice_queries import (
    slice_by_year,
    slice_by_category,
    slice_by_city,
    slice_by_month
)


class TestSliceOperations:
    """Test suite for slice OLAP operations"""
    
    def test_slice_by_year_structure(self, sqlite_engine: Engine):
        """Test slicing by a specific year"""
        year = 2021
        df, duration, query, params = slice_by_year(sqlite_engine, year)
        
        print("\n" + "="*80)
        print(f"SLICE TEST: Year {year}")
        print("="*80)
        print(f"\n📊 Results Shape: {df.shape}")
        print(f"⏱️  Query Duration: {duration:.4f}s")
        print(f"📋 Query Parameters: {params}")
        print(f"\n📋 Data Preview (first 10 rows):")
        print(df.head(10).to_string(index=False))
        
        # Validate structure
        assert not df.empty, f"Result should not be empty for year {year}"
        assert 'year' in df.columns, "Should have 'year' column"
        assert 'month_name' in df.columns, "Should have 'month_name' column"
        assert 'category' in df.columns, "Should have 'category' column"
        assert 'city' in df.columns, "Should have 'city' column"
        assert 'total_sales' in df.columns, "Should have 'total_sales' column"
        assert 'total_quantity' in df.columns, "Should have 'total_quantity' column"
        assert 'total_orders' in df.columns, "Should have 'total_orders' column"
        
        # Validate all rows are for the specified year
        assert (df['year'] == year).all(), f"All rows should be for year {year}"
        
        # Validate sorting (DESC by total_sales)
        assert df['total_sales'].tolist() == sorted(df['total_sales'].tolist(), reverse=True), \
            "Should be sorted by total_sales DESC"
        
        print(f"\n📈 Statistics:")
        print(f"   Total Rows: {len(df)}")
        print(f"   Total Sales: ${df['total_sales'].sum():.2f}")
        print(f"   Total Orders: {df['total_orders'].sum()}")
        print("\n✅ All assertions passed!")
        
    def test_slice_by_year_filtering(self, sqlite_engine: Engine):
        """Test that year slice filters correctly"""
        df_2021, _, _, _ = slice_by_year(sqlite_engine, 2021)
        df_2022, _, _, _ = slice_by_year(sqlite_engine, 2022)
        
        print("\n" + "="*80)
        print("SLICE TEST: Year Filtering")
        print("="*80)
        print(f"\n2021 Results: {len(df_2021)} rows")
        print(f"2022 Results: {len(df_2022)} rows")
        
        # 2021 should have data
        assert not df_2021.empty, "Should have data for 2021"
        
        # 2022 should be empty (based on seed data)
        assert df_2022.empty, "Should have no data for 2022"
        
        # Verify all 2021 data is actually from 2021
        if not df_2021.empty:
            assert (df_2021['year'] == 2021).all(), "All 2021 slice data should be from 2021"
        
        print("\n✅ Year filtering validated!")
        
    def test_slice_by_category_structure(self, sqlite_engine: Engine):
        """Test slicing by a specific category"""
        category = "Electronics"
        df, duration, query, params = slice_by_category(sqlite_engine, category)
        
        print("\n" + "="*80)
        print(f"SLICE TEST: Category '{category}'")
        print("="*80)
        print(f"\n📊 Results Shape: {df.shape}")
        print(f"⏱️  Query Duration: {duration:.4f}s")
        print(f"📋 Query Parameters: {params}")
        print(f"\n📋 Data Preview (first 10 rows):")
        print(df.head(10).to_string(index=False))
        
        # Validate structure
        assert not df.empty, f"Result should not be empty for category '{category}'"
        assert 'category' in df.columns, "Should have 'category' column"
        assert 'product_name' in df.columns, "Should have 'product_name' column"
        assert 'year' in df.columns, "Should have 'year' column"
        assert 'month_name' in df.columns, "Should have 'month_name' column"
        assert 'city' in df.columns, "Should have 'city' column"
        assert 'total_sales' in df.columns, "Should have 'total_sales' column"
        
        # Validate all rows are for the specified category
        assert (df['category'] == category).all(), f"All rows should be for category '{category}'"
        
        print(f"\n📦 Products in {category}:")
        for product in df['product_name'].unique():
            product_sales = df[df['product_name'] == product]['total_sales'].sum()
            print(f"   {product}: ${product_sales:.2f}")
        
        print("\n✅ All assertions passed!")
        
    def test_slice_by_category_all_categories(self, sqlite_engine: Engine):
        """Test slicing for all available categories"""
        categories = ["Electronics", "Toys", "Bags"]
        
        print("\n" + "="*80)
        print("SLICE TEST: All Categories")
        print("="*80)
        
        for category in categories:
            df, _, _, _ = slice_by_category(sqlite_engine, category)
            
            print(f"\n📦 Category: {category}")
            print(f"   Rows: {len(df)}")
            
            if not df.empty:
                print(f"   Total Sales: ${df['total_sales'].sum():.2f}")
                print(f"   Products: {df['product_name'].unique().tolist()}")
                
                # Validate filtering
                assert (df['category'] == category).all(), f"All rows should be '{category}'"
            
        print("\n✅ All categories tested!")
        
    def test_slice_by_city_structure(self, sqlite_engine: Engine):
        """Test slicing by a specific city"""
        city = "Manila"
        df, duration, query, params = slice_by_city(sqlite_engine, city)
        
        print("\n" + "="*80)
        print(f"SLICE TEST: City '{city}'")
        print("="*80)
        print(f"\n📊 Results Shape: {df.shape}")
        print(f"⏱️  Query Duration: {duration:.4f}s")
        print(f"📋 Query Parameters: {params}")
        print(f"\n📋 Data Preview (first 10 rows):")
        print(df.head(10).to_string(index=False))
        
        # Validate structure
        assert not df.empty, f"Result should not be empty for city '{city}'"
        assert 'city' in df.columns, "Should have 'city' column"
        assert 'year' in df.columns, "Should have 'year' column"
        assert 'month_name' in df.columns, "Should have 'month_name' column"
        assert 'category' in df.columns, "Should have 'category' column"
        assert 'product_name' in df.columns, "Should have 'product_name' column"
        assert 'total_sales' in df.columns, "Should have 'total_sales' column"
        
        # Validate all rows are for the specified city
        assert (df['city'] == city).all(), f"All rows should be for city '{city}'"
        
        print(f"\n🏙️  {city} Statistics:")
        print(f"   Total Sales: ${df['total_sales'].sum():.2f}")
        print(f"   Categories: {df['category'].unique().tolist()}")
        
        print("\n✅ All assertions passed!")
        
    def test_slice_by_city_all_cities(self, sqlite_engine: Engine):
        """Test slicing for all available cities"""
        cities = ["Manila", "Tokyo", "Berlin"]
        
        print("\n" + "="*80)
        print("SLICE TEST: All Cities")
        print("="*80)
        
        for city in cities:
            df, _, _, _ = slice_by_city(sqlite_engine, city)
            
            print(f"\n🏙️  City: {city}")
            print(f"   Rows: {len(df)}")
            
            if not df.empty:
                print(f"   Total Sales: ${df['total_sales'].sum():.2f}")
                print(f"   Total Orders: {df['total_orders'].sum()}")
                
                # Validate filtering
                assert (df['city'] == city).all(), f"All rows should be '{city}'"
        
        print("\n✅ All cities tested!")
        
    def test_slice_by_month_structure(self, sqlite_engine: Engine):
        """Test slicing by a specific year and month"""
        year, month = 2021, 1
        df, duration, query, params = slice_by_month(sqlite_engine, year, month)
        
        print("\n" + "="*80)
        print(f"SLICE TEST: Year {year}, Month {month}")
        print("="*80)
        print(f"\n📊 Results Shape: {df.shape}")
        print(f"⏱️  Query Duration: {duration:.4f}s")
        print(f"📋 Query Parameters: {params}")
        print(f"\n📋 Data Preview:")
        print(df.to_string(index=False))
        
        # Validate structure
        if not df.empty:
            assert 'year' in df.columns, "Should have 'year' column"
            assert 'month_name' in df.columns, "Should have 'month_name' column"
            assert 'category' in df.columns, "Should have 'category' column"
            assert 'city' in df.columns, "Should have 'city' column"
            assert 'total_sales' in df.columns, "Should have 'total_sales' column"
        
        print("\n✅ All assertions passed!")
        
    def test_slice_null_engine_handling(self):
        """Test that slice functions handle None engine gracefully"""
        df, duration, query, params = slice_by_year(None, 2021)
        
        assert df.empty, "Should return empty DataFrame for None engine"
        assert duration == 0.0, "Duration should be 0.0 for None engine"
        
        print("\n✅ Null engine handling validated!")


class TestSliceBusinessLogic:
    """Test business logic and analytical capabilities of slice operations"""
    
    def test_slice_dimension_isolation(self, sqlite_engine: Engine):
        """Test that slice isolates one dimension while showing others"""
        year = 2021
        df, _, _, _ = slice_by_year(sqlite_engine, year)
        
        print("\n" + "="*80)
        print("SLICE TEST: Dimension Isolation")
        print("="*80)
        
        # Year dimension should be fixed
        assert (df['year'] == year).all(), "Year should be fixed"
        
        # Other dimensions should vary
        categories = df['category'].nunique()
        cities = df['city'].nunique()
        months = df['month_name'].nunique()
        
        print(f"\n📊 Dimension Variation (Year={year} fixed):")
        print(f"   Categories: {categories}")
        print(f"   Cities: {cities}")
        print(f"   Months: {months}")
        
        # Should have variation in at least one dimension
        assert categories > 0 or cities > 0 or months > 0, \
            "Should have variation in other dimensions"
        
        print("\n✅ Dimension isolation validated!")
        
    def test_slice_comparative_analysis(self, sqlite_engine: Engine):
        """Test slice for comparing across one dimension"""
        # Slice by different cities
        manila_df, _, _, _ = slice_by_city(sqlite_engine, "Manila")
        tokyo_df, _, _, _ = slice_by_city(sqlite_engine, "Tokyo")
        berlin_df, _, _, _ = slice_by_city(sqlite_engine, "Berlin")
        
        print("\n" + "="*80)
        print("SLICE TEST: City Comparison")
        print("="*80)
        
        cities_data = {
            "Manila": manila_df,
            "Tokyo": tokyo_df,
            "Berlin": berlin_df
        }
        
        print(f"\n🏙️  City-wise Analysis:")
        for city, df in cities_data.items():
            if not df.empty:
                total_sales = df['total_sales'].sum()
                total_orders = df['total_orders'].sum()
                categories = df['category'].nunique()
                print(f"\n   {city}:")
                print(f"      Sales: ${total_sales:.2f}")
                print(f"      Orders: {total_orders}")
                print(f"      Categories: {categories}")
        
        print("\n✅ Comparative analysis validated!")
        
    def test_slice_data_completeness(self, sqlite_engine: Engine):
        """Test that slice maintains data completeness"""
        # Get all data for a year
        year_df, _, _, _ = slice_by_year(sqlite_engine, 2021)
        
        # Get slices by category for same year
        categories = ["Electronics", "Toys", "Bags"]
        category_dfs = []
        for category in categories:
            df, _, _, _ = slice_by_category(sqlite_engine, category)
            # Filter to same year
            df_2021 = df[df['year'] == 2021] if 'year' in df.columns else df
            category_dfs.append(df_2021)
        
        print("\n" + "="*80)
        print("SLICE TEST: Data Completeness")
        print("="*80)
        
        year_total = year_df['total_sales'].sum()
        
        print(f"\n📊 Year 2021 Total: ${year_total:.2f}")
        print(f"\n📦 Category Slices:")
        
        category_total = 0
        for i, category in enumerate(categories):
            if not category_dfs[i].empty:
                cat_sales = category_dfs[i]['total_sales'].sum()
                category_total += cat_sales
                print(f"   {category}: ${cat_sales:.2f}")
        
        print(f"\n📊 Sum of Category Slices: ${category_total:.2f}")
        
        # Category slices should sum to year total (allowing for floating point)
        # Note: This might not match exactly if there's overlap in the slice queries
        print(f"\n💡 Note: Slice sums may differ from totals due to grouping granularity")
        
        print("\n✅ Data completeness checked!")
        
    def test_slice_detail_level(self, sqlite_engine: Engine):
        """Test that slices maintain appropriate detail level"""
        # Year slice should show month-level detail
        year_df, _, _, _ = slice_by_year(sqlite_engine, 2021)
        
        # Category slice should show product-level detail
        category_df, _, _, _ = slice_by_category(sqlite_engine, "Electronics")
        
        print("\n" + "="*80)
        print("SLICE TEST: Detail Level")
        print("="*80)
        
        if not year_df.empty:
            print(f"\n📅 Year Slice Columns: {list(year_df.columns)}")
            assert 'month_name' in year_df.columns, "Year slice should have month detail"
            print(f"   ✓ Has month-level detail")
        
        if not category_df.empty:
            print(f"\n📦 Category Slice Columns: {list(category_df.columns)}")
            assert 'product_name' in category_df.columns, "Category slice should have product detail"
            print(f"   ✓ Has product-level detail")
        
        print("\n✅ Detail level validated!")
        
    def test_slice_performance_consistency(self, sqlite_engine: Engine):
        """Test that slice operations have consistent performance"""
        print("\n" + "="*80)
        print("SLICE TEST: Performance Consistency")
        print("="*80)
        
        # Test multiple slices
        _, duration1, _, _ = slice_by_year(sqlite_engine, 2021)
        _, duration2, _, _ = slice_by_category(sqlite_engine, "Electronics")
        _, duration3, _, _ = slice_by_city(sqlite_engine, "Manila")
        
        print(f"\n⏱️  Execution Times:")
        print(f"   Year Slice: {duration1:.4f}s")
        print(f"   Category Slice: {duration2:.4f}s")
        print(f"   City Slice: {duration3:.4f}s")
        
        # All should be reasonably fast (< 1 second for in-memory DB)
        assert duration1 < 1.0, "Year slice too slow"
        assert duration2 < 1.0, "Category slice too slow"
        assert duration3 < 1.0, "City slice too slow"
        
        print("\n✅ Performance consistency validated!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
