import os
from dotenv import load_dotenv
from etl.extract import extract_from_db
from etl.transform import (
    transform_dim_rider,
    transform_dim_customer,
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

def dim_customer():
    pass

def dim_product():
    pass
    
def dim_date():
    pass

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
    # dim_customer()
    # dim_product()
    # dim_date()
    
    fact_sales() 


if __name__ == "__main__":
    main()