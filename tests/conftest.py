import pathlib
import sys
from typing import Iterator
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# Ensure project root on sys.path so tests can import project modules
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def sqlite_engine() -> Iterator[Engine]:
    """In-memory SQLite engine with minimal schema and seed data for OLAP tests."""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    with engine.begin() as conn:
        # Create dimension tables
        conn.execute(text(
            """
            CREATE TABLE dim_user (
                user_key INTEGER PRIMARY KEY,
                continent TEXT,
                country TEXT,
                city TEXT,
                gender TEXT
            );
            """
        ))
        conn.execute(text(
            """
            CREATE TABLE dim_rider (
                rider_key INTEGER PRIMARY KEY,
                rider_name TEXT,
                vehicleType TEXT,
                gender TEXT,
                age INTEGER,
                courier_name TEXT
            );
            """
        ))
        conn.execute(text(
            """
            CREATE TABLE dim_product (
                product_key INTEGER PRIMARY KEY,
                product_name TEXT,
                category TEXT,
                product_code TEXT,
                price REAL
            );
            """
        ))
        conn.execute(text(
            """
            CREATE TABLE dim_date (
                date_key INTEGER PRIMARY KEY,
                full_date TEXT,
                day_name TEXT,
                month_name TEXT,
                day INTEGER,
                month INTEGER,
                quarter INTEGER,
                year INTEGER,
                is_weekend TEXT
            );
            """
        ))
        conn.execute(text(
            """
            CREATE TABLE fact_sales (
                order_number TEXT,
                customer_key INTEGER,
                product_key INTEGER,
                rider_key INTEGER,
                date_key INTEGER,
                quantity INTEGER,
                unit_price REAL,
                sales_amount REAL
            );
            """
        ))
        
        # Seed dim_user
        conn.execute(text(
            """
            INSERT INTO dim_user (user_key, continent, country, city, gender) VALUES
            (1, 'Asia', 'Philippines', 'Manila', 'Male'),
            (2, 'Asia', 'Japan', 'Tokyo', 'Female'),
            (3, 'Europe', 'Germany', 'Berlin', 'Female');
            """
        ))
        
        # Seed dim_rider
        conn.execute(text(
            """
            INSERT INTO dim_rider (rider_key, rider_name, vehicleType, gender, age, courier_name) VALUES
            (100, 'John Doe', 'Motorcycle', 'Male', 28, 'FEDEX'),
            (101, 'Jane Smith', 'Bicycle', 'Female', 32, 'DHL'),
            (102, 'Bob Lee', 'Car', 'Male', 45, 'UPS');
            """
        ))
        
        # Seed dim_product
        conn.execute(text(
            """
            INSERT INTO dim_product (product_key, product_name, category, product_code, price) VALUES
            (10, 'Laptop', 'Electronics', 'P001', 1200.0),
            (11, 'Toy Car', 'Toys', 'P002', 15.0),
            (12, 'Handbag', 'Bags', 'P003', 60.0);
            """
        ))
        
        # Seed dim_date
        conn.execute(text(
            """
            INSERT INTO dim_date (date_key, full_date, day_name, month_name, day, month, quarter, year, is_weekend) VALUES
            (20210102, '2021-01-02', 'Saturday', 'January', 2, 1, 1, 2021, 'Y'),
            (20210103, '2021-01-03', 'Sunday', 'January', 3, 1, 1, 2021, 'Y'),
            (20210510, '2021-05-10', 'Monday', 'May', 10, 5, 2, 2021, 'N');
            """
        ))
        
        # Seed fact_sales (note repeated order_numbers for DISTINCT counting)
        conn.execute(text(
            """
            INSERT INTO fact_sales (order_number, customer_key, product_key, rider_key, date_key, quantity, unit_price, sales_amount) VALUES
            ('ORD-1', 1, 10, 100, 20210102, 2, 50.0, 100.0),
            ('ORD-2', 1, 11, 101, 20210103, 3, 20.0, 200.0),
            ('ORD-2', 1, 12, 101, 20210103, 1, 50.0, 50.0),
            ('ORD-3', 2, 10, 102, 20210510, 5, 60.0, 300.0),
            ('ORD-4', 3, 11, 100, 20210102, 2, 200.0, 400.0);
            """
        ))
    try:
        yield engine
    finally:
        engine.dispose()
