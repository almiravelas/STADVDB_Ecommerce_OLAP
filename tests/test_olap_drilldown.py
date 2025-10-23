"""
Tests for Drill-down OLAP Operations
Tests disaggregation to lower levels of granularity
"""
import pytest
import pandas as pd
from sqlalchemy.engine import Engine

# Import drilldown query functions
import sys
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.queries.drilldown_queries import (
    drilldown_year_to_month,
    drilldown_month_to_day,
    drilldown_category_to_product,
    drilldown_region_to_country
)


class TestDrilldownOperations:
    """Test suite for drill-down OLAP operations"""
    
    def test_drilldown_year_to_month_structure(self, sqlite_engine: Engine):
        """Test drilling down from year to month level"""
        year = 2021
        df, duration, query, params = drilldown_year_to_month(sqlite_engine, year)
        
        print("\n" + "="*80)
        print(f"DRILLDOWN TEST: Year {year} to Month")
        print("="*80)
        print(f"\n📊 Results Shape: {df.shape}")
        print(f"⏱️  Query Duration: {duration:.4f}s")
        print(f"📋 Query Parameters: {params}")
        print(f"\n📋 Data Preview:")
        print(df.to_string(index=False))
        
        # Validate structure
        assert not df.empty, "Result should not be empty for year 2021"
        assert 'year' in df.columns, "Should have 'year' column"
        assert 'month' in df.columns, "Should have 'month' column"
        assert 'month_name' in df.columns, "Should have 'month_name' column"
        assert 'total_sales' in df.columns, "Should have 'total_sales' column"
        
        # Validate all rows are for requested year
        assert (df['year'] == year).all(), f"All rows should be for year {year}"
        
        # Validate month values
        assert df['month'].min() >= 1, "Month should be at least 1"
        assert df['month'].max() <= 12, "Month should be at most 12"
        
        # Validate sorting
        assert df['month'].tolist() == sorted(df['month'].tolist()), \
            "Should be sorted by month"
        
        print("\n✅ All assertions passed!")
        
    def test_drilldown_year_to_month_filtering(self, sqlite_engine: Engine):
        """Test that year filter works correctly"""
        df_2021, _, _, _ = drilldown_year_to_month(sqlite_engine, 2021)
        df_2022, _, _, _ = drilldown_year_to_month(sqlite_engine, 2022)
        
        print("\n" + "="*80)
        print("DRILLDOWN TEST: Year Filtering")
        print("="*80)
        print(f"\n2021 Results: {len(df_2021)} rows")
        print(f"2022 Results: {len(df_2022)} rows")
        
        # 2021 should have data
        assert not df_2021.empty, "Should have data for 2021"
        
        # 2022 should have no data (based on seed data)
        assert df_2022.empty, "Should have no data for 2022"
        
        print("\n✅ Year filtering validated!")
        
    def test_drilldown_month_to_day_structure(self, sqlite_engine: Engine):
        """Test drilling down from month to day level"""
        year, month = 2021, 1
        df, duration, query, params = drilldown_month_to_day(sqlite_engine, year, month)
        
        print("\n" + "="*80)
        print(f"DRILLDOWN TEST: Year {year}, Month {month} to Day")
        print("="*80)
        print(f"\n📊 Results Shape: {df.shape}")
        print(f"⏱️  Query Duration: {duration:.4f}s")
        print(f"📋 Query Parameters: {params}")
        print(f"\n📋 Data Preview:")
        print(df.to_string(index=False))
        
        # Validate structure
        assert not df.empty, "Result should not be empty for 2021-01"
        assert 'full_date' in df.columns, "Should have 'full_date' column"
        assert 'day_name' in df.columns, "Should have 'day_name' column"
        assert 'is_weekend' in df.columns, "Should have 'is_weekend' column"
        assert 'total_sales' in df.columns, "Should have 'total_sales' column"
        
        # Validate is_weekend values
        assert set(df['is_weekend']) <= {'Y', 'N'}, "is_weekend should be Y or N"
        
        # Validate sorting
        assert df['full_date'].tolist() == sorted(df['full_date'].tolist()), \
            "Should be sorted by date"
        
        print("\n✅ All assertions passed!")
        
    def test_drilldown_month_to_day_filtering(self, sqlite_engine: Engine):
        """Test that month filter works correctly"""
        df_jan, _, _, _ = drilldown_month_to_day(sqlite_engine, 2021, 1)
        df_may, _, _, _ = drilldown_month_to_day(sqlite_engine, 2021, 5)
        df_dec, _, _, _ = drilldown_month_to_day(sqlite_engine, 2021, 12)
        
        print("\n" + "="*80)
        print("DRILLDOWN TEST: Month Filtering")
        print("="*80)
        print(f"\n2021-01 Results: {len(df_jan)} rows")
        print(f"2021-05 Results: {len(df_may)} rows")
        print(f"2021-12 Results: {len(df_dec)} rows")
        
        # January should have data (seed data has dates in January)
        assert not df_jan.empty, "Should have data for January 2021"
        
        # May should have data (seed data has date in May)
        assert not df_may.empty, "Should have data for May 2021"
        
        # December should have no data
        assert df_dec.empty, "Should have no data for December 2021"
        
        print("\n✅ Month filtering validated!")
        
    def test_drilldown_category_to_product_structure(self, sqlite_engine: Engine):
        """Test drilling down from category to product level"""
        category = "Electronics"
        df, duration, query, params = drilldown_category_to_product(sqlite_engine, category)
        
        print("\n" + "="*80)
        print(f"DRILLDOWN TEST: Category '{category}' to Product")
        print("="*80)
        print(f"\n📊 Results Shape: {df.shape}")
        print(f"⏱️  Query Duration: {duration:.4f}s")
        print(f"📋 Query Parameters: {params}")
        print(f"\n📋 Data Preview:")
        print(df.to_string(index=False))
        
        # Validate structure
        assert not df.empty, f"Result should not be empty for category '{category}'"
        assert 'category' in df.columns, "Should have 'category' column"
        assert 'product_name' in df.columns, "Should have 'product_name' column"
        assert 'price' in df.columns, "Should have 'price' column"
        assert 'total_sales' in df.columns, "Should have 'total_sales' column"
        
        # Validate all rows are for requested category
        assert (df['category'] == category).all(), f"All rows should be for category '{category}'"
        
        # Validate sorting (should be DESC by total_sales)
        assert df['total_sales'].tolist() == sorted(df['total_sales'].tolist(), reverse=True), \
            "Should be sorted by total_sales DESC"
        
        print("\n✅ All assertions passed!")
        
    def test_drilldown_category_to_product_all_categories(self, sqlite_engine: Engine):
        """Test drilling down for all categories"""
        categories = ["Electronics", "Toys", "Bags"]
        
        print("\n" + "="*80)
        print("DRILLDOWN TEST: All Categories to Products")
        print("="*80)
        
        for category in categories:
            df, _, _, _ = drilldown_category_to_product(sqlite_engine, category)
            
            print(f"\n📦 Category: {category}")
            print(f"   Products: {len(df)}")
            
            if not df.empty:
                print(f"   Products: {df['product_name'].tolist()}")
                assert (df['category'] == category).all(), f"Filtering failed for {category}"
        
        print("\n✅ All categories tested!")
        
    def test_drilldown_region_to_country_structure(self, sqlite_engine: Engine):
        """Test drilling down from region to country level"""
        continent = "Asia"
        df, duration, query, params = drilldown_region_to_country(sqlite_engine, continent)
        
        print("\n" + "="*80)
        print(f"DRILLDOWN TEST: Region '{continent}' to Country")
        print("="*80)
        print(f"\n📊 Results Shape: {df.shape}")
        print(f"⏱️  Query Duration: {duration:.4f}s")
        print(f"📋 Query Parameters: {params}")
        print(f"\n📋 Data Preview:")
        print(df.to_string(index=False))
        
        # Validate structure
        assert not df.empty, f"Result should not be empty for continent '{continent}'"
        assert 'continent' in df.columns, "Should have 'continent' column"
        assert 'country' in df.columns, "Should have 'country' column"
        assert 'total_sales' in df.columns, "Should have 'total_sales' column"
        
        # Validate all rows are for requested continent
        assert (df['continent'] == continent).all(), f"All rows should be for continent '{continent}'"
        
        # Validate countries from seed data
        countries = set(df['country'].tolist())
        expected_countries = {'Philippines', 'Japan'}
        assert countries == expected_countries, f"Expected {expected_countries}, got {countries}"
        
        print(f"\n🌏 Countries in {continent}: {countries}")
        print("\n✅ All assertions passed!")
        
    def test_drilldown_null_engine_handling(self):
        """Test that drilldown functions handle None engine gracefully"""
        df, duration, query, params = drilldown_year_to_month(None, 2021)
        
        assert df.empty, "Should return empty DataFrame for None engine"
        assert duration == 0.0, "Duration should be 0.0 for None engine"
        
        print("\n✅ Null engine handling validated!")


class TestDrilldownBusinessLogic:
    """Test business logic and data correctness in drilldown operations"""
    
    def test_drilldown_aggregation_consistency(self, sqlite_engine: Engine):
        """Test that drill-down maintains aggregation consistency"""
        # Get year total
        from app.queries.rollup_queries import rollup_sales_by_year
        
        year_df, _, _, _ = rollup_sales_by_year(sqlite_engine)
        year_2021_sales = year_df[year_df['year'] == 2021]['total_sales'].iloc[0]
        
        # Get month totals for same year
        month_df, _, _, _ = drilldown_year_to_month(sqlite_engine, 2021)
        months_total_sales = month_df['total_sales'].sum()
        
        print("\n" + "="*80)
        print("DRILLDOWN TEST: Aggregation Consistency")
        print("="*80)
        print(f"\n📊 Year 2021 Total: ${year_2021_sales:.2f}")
        print(f"📊 Sum of Months: ${months_total_sales:.2f}")
        
        # Should be equal (allowing small floating point difference)
        assert abs(year_2021_sales - months_total_sales) < 0.01, \
            f"Aggregation inconsistency: {year_2021_sales} vs {months_total_sales}"
        
        print("\n✅ Aggregation consistency validated!")
        
    def test_drilldown_progressive_detail(self, sqlite_engine: Engine):
        """Test that each drill-down level provides more detail"""
        # Year level
        year_df, _, _, _ = drilldown_year_to_month(sqlite_engine, 2021)
        year_rows = len(year_df)
        
        # Month level (for first month with data)
        first_month = year_df['month'].iloc[0]
        day_df, _, _, _ = drilldown_month_to_day(sqlite_engine, 2021, first_month)
        day_rows = len(day_df)
        
        print("\n" + "="*80)
        print("DRILLDOWN TEST: Progressive Detail")
        print("="*80)
        print(f"\n📊 Month-level rows: {year_rows}")
        print(f"📊 Day-level rows: {day_rows}")
        
        # Day level should have at least as many rows as we have distinct days
        assert day_rows > 0, "Day level should have data"
        
        print("\n✅ Progressive detail validated!")
        
    def test_drilldown_data_completeness(self, sqlite_engine: Engine):
        """Test that drill-down doesn't lose data"""
        year = 2021
        
        # Get all months for year
        month_df, _, _, _ = drilldown_year_to_month(sqlite_engine, year)
        
        print("\n" + "="*80)
        print("DRILLDOWN TEST: Data Completeness")
        print("="*80)
        print(f"\n📊 Months with data: {len(month_df)}")
        
        # Each month should have positive sales
        assert (month_df['total_sales'] > 0).all(), "All months should have positive sales"
        assert (month_df['total_orders'] > 0).all(), "All months should have orders"
        
        print(f"📊 Total orders: {month_df['total_orders'].sum()}")
        print(f"📊 Total sales: ${month_df['total_sales'].sum():.2f}")
        print("\n✅ Data completeness validated!")
        
    def test_drilldown_weekend_analysis(self, sqlite_engine: Engine):
        """Test weekend vs weekday analysis in day-level drill-down"""
        df, _, _, _ = drilldown_month_to_day(sqlite_engine, 2021, 1)
        
        print("\n" + "="*80)
        print("DRILLDOWN TEST: Weekend Analysis")
        print("="*80)
        
        if not df.empty:
            weekend_sales = df[df['is_weekend'] == 'Y']['total_sales'].sum()
            weekday_sales = df[df['is_weekend'] == 'N']['total_sales'].sum()
            
            print(f"\n📊 Weekend Sales: ${weekend_sales:.2f}")
            print(f"📊 Weekday Sales: ${weekday_sales:.2f}")
            
            # Should have is_weekend flag
            assert 'is_weekend' in df.columns, "Should have is_weekend column"
            
            print("\n✅ Weekend analysis validated!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
