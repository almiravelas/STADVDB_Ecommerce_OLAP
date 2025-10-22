# Functional Testing Plan

This document explains, for each test type, the rationale/purpose, the process (how we test), the data we use, and the results we expect. It directly answers:

- How did you validate the correctness of your ETL script? Procedure and test cases.
- How did you validate the correctness of your OLAP operations? Procedure and test cases.

## Scope

- ETL transforms
  - `etl/transform/dim_user.py: transform_dim_user`
  - `etl/transform/fact_sales.py: transform_fact_sales`
  - `etl/transform/dim_date.py: transform_dim_date`
  - `etl/transform/dim_product.py: transform_dim_product`
  - `etl/transform/dim_rider.py: transform_dim_rider`
- OLAP queries
  - `app/queries/user_queries.py: get_user_data, get_distinct_user_attributes`
  - `app/queries/rider_queries.py: get_sales_for_dashboard`
  - `app/queries/product_queries.py: get_dashboard_product_data`
  - `app/queries/sales_queries.py: get_sales_per_month, get_sales_per_year, get_sales_weekend_vs_weekday, get_sales_by_day_of_week, get_daily_sales_trend`
  - Dashboard analytics: KPI aggregations, top performers, multi-dimensional trends

## How to run tests

- Install deps
  - `pip install -r requirements.txt`
- Run
  - `pytest -q`

---

## ETL Tests

### 1) transform_dim_user

- Rationale / Purpose
  - Validate the user dimension produces stable keys and normalized attributes (gender, city, country, continent, signup_date) required for joins and OLAP filters.
- Test Process
  - Unit test with a tiny in-memory DataFrame (no DB needed).
  - Verify required columns exist and are correctly populated.
  - Verify gender standardization and continent mapping fallback.
  - Verify deduplication and signup_date parsing.
- Test Data
  - Sample rows with fields: `id`, `username`, `firstName`, `lastName`, `gender`, `city`, `country`, `createdAt`.
  - Include mixed-case values and missing entries to test normalization and defaults.
- Test Results
  - Output includes columns: `user_key, username, full_name, gender, city, country, continent, signup_date`.
  - `user_key` non-null; `gender` standardized to Male/Female/Other; `continent` filled; `signup_date` parsed or NaT.

### 2) transform_fact_sales

- Rationale / Purpose
  - Ensure the sales fact table computes measures (`sales_amount`) and standardizes keys/renames needed by downstream OLAP queries, with correct date_key.
- Test Process
  - Unit test with a minimal DataFrame; validate renames and computed measures.
  - Validate `date_key` is normalized to integer `YYYYMMDD` using the shared date parser.
  - Validate numeric coercions and NaN handling do not drop essential keys.
- Test Data
  - Rows with: `quantity`, `price`, `orderNumber`, `userId`, `ProductId`, `deliveryRiderId`, `deliveryDate`.
  - Use two orders and distinct users to verify mapping and measure.
- Test Results
  - Columns present: `customer_key, product_key, rider_key, date_key, order_number, quantity, unit_price, sales_amount`.
  - `sales_amount = quantity * unit_price` and `date_key` integer of form `YYYYMMDD`.

### 3) transform_dim_date

- Rationale / Purpose
  - Confirm the date dimension derives attributes used by the app (year, month_name, day_name, weekend flag) and produces a `date_key` surrogate key.
- Test Process
  - Unit test with a few target dates; verify derived columns and correctness.
- Test Data
  - 3–5 `full_date` values across months/years, including a weekend.
- Test Results
  - Columns present: `date_key, full_date, day_name, month_name, day, month, year, is_weekend`.
  - Year/month/day correct; weekend flag matches calendar.

---

## OLAP Tests

### get_user_data

- Rationale / Purpose
  - Validate the correctness of pre-aggregations (SUM sales_amount, COUNT DISTINCT order_number) and that filters for continent/country/city/gender behave as intended.
- Test Process
  - Use an in-memory SQLite database via SQLAlchemy; create tables `dim_user` and `fact_sales`.
  - Seed a small fixture with 3 users and 5 fact rows (including repeated `order_number` for distinct counting).
  - Run `get_user_data` with and without filters; assert totals and row counts.
- Test Data
  - `dim_user`: `user_key, continent, country, city, gender`.
  - `fact_sales`: `order_number, customer_key, sales_amount`.
- Test Results
  - No filters: 1 row per user present in both tables; expected sums; DISTINCT order count correct.
  - With filters: subsets match the seeded demographics; totals match hand calculations.

### get_distinct_user_attributes

- Rationale / Purpose
  - Ensure the filter list options shown in the UI exactly reflect the stored dimension values.
- Test Process
  - Query the same SQLite fixture; assert the distinct lists match seeded values.
- Test Data
  - Reuse the `dim_user` fixture from above.
- Test Results
  - Returned dict has keys `continents, countries, cities, genders` and the values contain exactly the seeded attribute values.

---

## Additional ETL Tests

### 4) transform_dim_product

- Rationale / Purpose
  - Validate product dimension standardizes categories and removes duplicates while preserving essential attributes.
- Test Process
  - Unit test with DataFrame containing duplicate products and various category names.
  - Verify deduplication logic and category normalization.
- Test Data
  - Rows with: `id, name, Category, Quantity` including duplicates and mixed-case categories.
- Test Results
  - Columns present: `product_key, product_name, category, quantity_in_stock`.
  - Categories normalized (GADGETS→Electronics, toys→Toys).
  - Duplicates removed (6 rows → 5 unique products).

### 5) transform_dim_rider

- Rationale / Purpose
  - Ensure rider dimension standardizes vehicle types, genders, and courier names for consistent analysis.
- Test Process
  - Unit test with DataFrame containing various vehicle types and courier names including typos.
  - Validate standardization logic and typo corrections.
- Test Data
  - Rows with: `id, fullName, Gender, VehicleType, CourierName` with mixed formats.
- Test Results
  - Columns present: `rider_key, rider_name, gender, vehicle_type, courier_name`.
  - Vehicle types standardized (motorbike→Motorcycle, van→Van).
  - Genders standardized (M→Male, f→Female).
  - Courier typos corrected (FEDEZ→FEDEX).

---

## Additional OLAP Tests

### get_sales_for_dashboard (Rider Analytics)

- Rationale / Purpose
  - Validate rider performance aggregations with order-level metrics.
- Test Process
  - Use SQLite fixture with riders, dates, and sales data.
  - Verify order aggregation and multi-table joins.
- Test Data
  - Seed data: 3 riders, 5 sales transactions, 3 dates.
- Test Results
  - Returns rider_key, rider_name, order_number, full_date, sales_amount.
  - Correct JOINs across fact_sales, dim_rider, dim_date.

### get_dashboard_product_data

- Rationale / Purpose
  - Validate product+date aggregations for dashboard visualizations.
- Test Process
  - Query aggregates products by date with sales totals.
- Test Data
  - 3 products, multiple dates, 5 sales transactions.
- Test Results
  - Returns product_key, product_name, category, full_date, total_sales.
  - Aggregations match expected totals by product and date.

### get_sales_per_month / get_sales_per_year

- Rationale / Purpose
  - Validate time-series aggregations for trend analysis.
- Test Process
  - Test monthly and yearly rollups from daily sales.
- Test Data
  - Sales spanning multiple months in 2021.
- Test Results
  - Monthly: Returns year, month, month_name, total_sales.
  - Yearly: Returns year, total_sales.
  - Totals match seeded data.

### get_sales_weekend_vs_weekday

- Rationale / Purpose
  - Validate temporal segmentation using weekend flags.
- Test Process
  - Aggregate sales by is_weekend flag.
- Test Data
  - Sales on Saturday, Sunday (weekend) and Monday (weekday).
- Test Results
  - Returns is_weekend, total_sales.
  - Weekend total = $750, Weekday total = $300.

### get_sales_by_day_of_week

- Rationale / Purpose
  - Validate day-of-week aggregations for staffing/inventory planning.
- Test Process
  - Group sales by day_name and aggregate totals.
- Test Data
  - Sales on Monday, Saturday, Sunday.
- Test Results
  - Returns day_name, total_sales.
  - Saturday = $500, Sunday = $250, Monday = $300.

### get_daily_sales_trend

- Rationale / Purpose
  - Provide daily time-series data for trend visualization and forecasting.
- Test Process
  - Query daily aggregates sorted chronologically.
- Test Data
  - 3 distinct dates with sales.
- Test Results
  - Returns full_date, total_sales.
  - Dates sorted chronologically, total = $1,050.

### Dashboard KPI Aggregations

- Rationale / Purpose
  - Calculate core business metrics for dashboard overview.
- Test Process
  - Direct SQL queries for counts, sums, and averages.
- Test Data
  - Complete star schema with 5 sales transactions.
- Test Results
  - Total orders: 4, Total sales: $1,050, Avg order value: $262.50.
  - Customer count: 3, Rider count: 3, Product count: 3.

### Dashboard Top Performers

- Rationale / Purpose
  - Identify top customers, riders, and products by sales volume.
- Test Process
  - Rank entities by sales/delivery totals.
- Test Data
  - Users, riders, products with varying transaction volumes.
- Test Results
  - Top customer: User 3 ($400), Top rider: John Doe ($500).
  - Top product: Toy Car ($600 revenue).

### Dashboard Monthly Trend (Multi-dimensional)

- Rationale / Purpose
  - Monthly sales broken down by category and courier.
- Test Process
  - Multi-dimensional aggregations by month + category/courier.
- Test Data
  - Sales in January (3 orders) and May (1 order).
- Test Results
  - By category: January Toys = $600, January Electronics = $100, etc.
  - By courier: FEDEX = $500 (2 orders), DHL = $250, UPS = $300.

---

## Sample Expected Outcome

- ETL tests: all PASS (5/5)
  - `sales_amount` computed correctly; required columns present
  - `date_key` integer format validated
  - Gender/continent/category/vehicle/courier normalized
  - Duplicates removed, whitespace trimmed
- OLAP tests: all PASS (13/13)
  - SUM and DISTINCT logic validated
  - Multi-table JOINs verified across all dimensions
  - Filter permutations return correct subsets
  - Time-series aggregations (daily, monthly, yearly, day-of-week)
  - Dashboard KPIs calculated correctly
  - Top performer rankings accurate
  - Multi-dimensional analysis validated

**Total: 18 tests, 100% pass rate**

If a test fails, the assertion messages will indicate which column/aggregation didn't match, guiding fixes in the corresponding transform/query.

