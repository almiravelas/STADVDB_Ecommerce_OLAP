from .transform import (
    transform_dim_rider,
    transform_dim_customer,
    transform_dim_product,
    transform_dim_date,
    transform_fact_sales
)

def run_all_transforms(raw_data: dict) -> dict:
    print("\n--- Starting Transformation Stage ---")

    dim_rider = transform_dim_rider(raw_data.get('riders'))
    dim_customer = transform_dim_customer(raw_data.get('customers'))
    dim_product = transform_dim_product(raw_data.get('products'))
    dim_date = transform_dim_date(raw_data.get('sales')) 

    fact_sales = transform_fact_sales(raw_data.get('sales'))

    print("\n--- Transformation Stage Complete ---\n")

    return {
        'dim_rider': dim_rider,
        'dim_customer': dim_customer,
        'dim_product': dim_product,
        'dim_date': dim_date,
        'fact_sales': fact_sales
    }