# STADVDB_MCO1

Make sure to create schema of faker (MCO1 dataset) and sales_wh (Our data warehouse)

Import data of MCO1 dataset

pip install -r requirements.txt
python main.py
python -m streamlit run app.py

## Testing

- Plan: see `docs/TESTING.md` for rationale, process, test data, and results.
- Results: see `docs/TEST_RESULTS.md` for actual before/after transformation outputs and query results.
- Run:
  - Install: `pip install -r requirements.txt`
  - Execute: `pytest -q` (quick) or `pytest -v -s` (verbose with output)
- Coverage:
  - ETL: `etl/transform/dim_user.py`, `etl/transform/fact_sales.py`, `etl/transform/dim_date.py`, `etl/transform/dim_product.py`, `etl/transform/dim_rider.py`
  - OLAP: `app/queries/user_queries.py`, `app/queries/rider_queries.py`, `app/queries/product_queries.py`, `app/queries/sales_queries.py` (date queries), dashboard analytics
- Status: ✅ All 18 tests passing
