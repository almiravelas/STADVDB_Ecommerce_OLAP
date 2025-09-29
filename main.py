import os
from dotenv import load_dotenv
from src.extract import extract_from_db
from src.transform import (
    transform_dim_rider,
    transform_dim_customer,
    transform_dim_product,
    transform_dim_date,
    transform_fact_sales
)
from src.load import load_to_warehouse

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
    load_to_warehouse(transformed_df, "dim_rider")

def dim_customer():
    pass

def dim_product():
    pass
    
def dim_date():
    pass

def fact_sales():
    pass


def main():
    # fact and dimensions (uncomment when done)
    dim_rider()
    # dim_customer()
    # dim_product()
    # dim_date()
    
    # fact_sales() 


if __name__ == "__main__":
    main()