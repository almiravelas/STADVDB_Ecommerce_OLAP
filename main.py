import os
import pandas as pd
from dotenv import load_dotenv
from etl.extract import extract_from_db
from etl.transform import (
    transform_dim_rider,
    transform_dim_user,
    transform_dim_product,
    transform_dim_date,
    transform_fact_sales
)
from etl.load import load_to_warehouse

# load .env
load_dotenv()

def dim_rider(): # Aza WIP
    """Extracts, transforms, and loads the rider dimension."""
    print("\n[DIMENSION] Processing Rider Dimension...")
    rider_query = """
        SELECT 
            r.id, 
            CONCAT(r.firstName, ' ', r.lastName) AS rider_name, 
            r.vehicleType,
            r.age,
            r.gender,
            c.name AS courier_name
        FROM riders r
        LEFT JOIN couriers c ON r.courierId = c.id;
    """
    source_df = extract_from_db(rider_query)
    transformed_df = transform_dim_rider(source_df)

    print("--- Transformed dim_rider sample ---")
    print(transformed_df.head())
    
    load_to_warehouse(transformed_df, "dim_rider")

def dim_user():
    print("\n[DIMENSION] Processing User Dimension...")
    # This query gets all columns from your source 'users' table
    user_query = """
        SELECT 
            id,
            username,
            firstName,
            lastName,
            gender,
            city,
            country,
            createdAt
        FROM users;
    """
    source_df = extract_from_db(user_query)
    # This calls your transformation logic from dim_user.py
    transformed_df = transform_dim_user(source_df)

    print("--- Transformed dim_user sample ---")
    print(transformed_df.head())
    
    # This loads the final data into the 'dim_user' table
    load_to_warehouse(transformed_df, "dim_user")


def dim_product():
    print("\n[DIMENSION] Processing Product Dimension...")

    product_query = """
        SELECT 
            p.ID,
            p.Name,
            p.Category,
            p.ProductCode,
            p.Price,
            p.CreatedAt,
            p.UpdatedAt
        FROM products p;
    """
    source_df = extract_from_db(product_query)
    transformed_df = transform_dim_product(source_df)

    print("--- Transformed dim_product sample ---")
    print(transformed_df.head())

    load_to_warehouse(transformed_df, "dim_product")
    
def dim_date():
    print("\n[DIMENSION] Processing Date Dimension...")

    # Define your date range (you can adjust as needed)
    start_date = "2020-01-01"
    end_date = "2030-12-31"

    # Create a DataFrame of all dates within the range
    date_range = pd.date_range(start=start_date, end=end_date)
    source_df = pd.DataFrame({'full_date': date_range})

    # Transform into dimension format
    transformed_df = transform_dim_date(source_df)

    print("--- Transformed dim_date sample ---")
    print(transformed_df.head())

    # Load into the warehouse
    load_to_warehouse(transformed_df, "dim_date")

def fact_sales():
    print("\n[FACT] Processing Sales Fact...")
    sales_query = """
        SELECT
            oi.quantity,
            p.price,
            o.orderNumber,
            o.userId,
            oi.ProductId,
            o.deliveryRiderId,
            o.deliveryDate
        FROM orderitems oi
        LEFT JOIN orders o ON oi.OrderId = o.id
        LEFT JOIN products p ON oi.ProductId = p.id;
    """
    source_df = extract_from_db(sales_query)
    transformed_df = transform_fact_sales(source_df)
    
    print("--- Transformed fact_sales sample ---")
    print(transformed_df.head())

    load_to_warehouse(transformed_df, "fact_sales")


def main():
    # fact and dimensions (uncomment when done)
     dim_rider() 
     dim_user()
     dim_product()
     dim_date()
    
     fact_sales() 

if __name__ == "__main__":
    main()