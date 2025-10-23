"""
Script to create all recommended indexes for query optimization
Run this script to apply indexes to your database

WARNING: Always backup your database before running this script!
"""
from utils.db_connection import get_warehouse_engine
from sqlalchemy import text
import time


def create_indexes():
    """Create all recommended indexes"""
    engine = get_warehouse_engine()
    
    if engine is None:
        print("❌ Failed to connect to database")
        return
    
    print("="*70)
    print("🔧 Creating Recommended Indexes")
    print("="*70)
    print()
    
    # List of index creation statements
    indexes = [
        {
            "name": "ix_fs_date_key",
            "sql": "CREATE INDEX ix_fs_date_key ON fact_sales(date_key);",
            "description": "Index on fact_sales.date_key for date filtering"
        },
        {
            "name": "ix_fs_product_key",
            "sql": "CREATE INDEX ix_fs_product_key ON fact_sales(product_key);",
            "description": "Index on fact_sales.product_key for product joins"
        },
        {
            "name": "ix_fs_customer_key",
            "sql": "CREATE INDEX ix_fs_customer_key ON fact_sales(customer_key);",
            "description": "Index on fact_sales.customer_key for user joins"
        },
        {
            "name": "ix_fs_rider_key",
            "sql": "CREATE INDEX ix_fs_rider_key ON fact_sales(rider_key);",
            "description": "Index on fact_sales.rider_key for rider joins"
        },
        {
            "name": "ix_fs_order_number",
            "sql": "CREATE INDEX ix_fs_order_number ON fact_sales(order_number);",
            "description": "Index on fact_sales.order_number for COUNT(DISTINCT)"
        },
        {
            "name": "ix_dp_category",
            "sql": "CREATE INDEX ix_dp_category ON dim_product(category);",
            "description": "Index on dim_product.category for category filtering"
        },
        {
            "name": "ix_dr_courier",
            "sql": "CREATE INDEX ix_dr_courier ON dim_rider(courier_name);",
            "description": "Index on dim_rider.courier_name for courier filtering"
        },
        {
            "name": "ix_du_city",
            "sql": "CREATE INDEX ix_du_city ON dim_user(city);",
            "description": "Index on dim_user.city for city filtering"
        },
        {
            "name": "ix_fs_composite_date_product",
            "sql": "CREATE INDEX ix_fs_composite_date_product ON fact_sales(date_key, product_key);",
            "description": "Composite index for date + product queries"
        }
    ]
    
    created = 0
    skipped = 0
    failed = 0
    
    for idx in indexes:
        print(f"Creating: {idx['name']}")
        print(f"  Purpose: {idx['description']}")
        
        try:
            start_time = time.time()
            
            with engine.connect() as conn:
                # Use raw connection to commit
                with conn.begin():
                    conn.execute(text(idx['sql']))
            
            duration = time.time() - start_time
            print(f"  ✅ Created successfully in {duration:.2f}s")
            created += 1
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if index already exists
            if "Duplicate key name" in error_msg or "already exists" in error_msg.lower():
                print(f"  ⏭️  Already exists - skipping")
                skipped += 1
            else:
                print(f"  ❌ Failed: {error_msg}")
                failed += 1
        
        print()
    
    # Summary
    print("="*70)
    print("📊 Index Creation Summary")
    print("="*70)
    print(f"✅ Created: {created}")
    print(f"⏭️  Skipped (already exist): {skipped}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Total: {len(indexes)}")
    print()
    
    if created > 0 or skipped > 0:
        print("="*70)
        print("🔍 Next Steps:")
        print("="*70)
        print("1. Update database statistics:")
        print("   ANALYZE TABLE fact_sales;")
        print("   ANALYZE TABLE dim_product;")
        print("   ANALYZE TABLE dim_rider;")
        print("   ANALYZE TABLE dim_user;")
        print()
        print("2. Verify indexes were created:")
        print("   python check_indexes.py")
        print()
        print("3. Test query performance in EXPLAIN tab of the app")
        print()
    
    if failed > 0:
        print("⚠️  Some indexes failed to create. Review errors above.")


def analyze_tables():
    """Run ANALYZE TABLE on all tables to update statistics"""
    engine = get_warehouse_engine()
    
    if engine is None:
        print("❌ Failed to connect to database")
        return
    
    print("="*70)
    print("📊 Updating Table Statistics (ANALYZE)")
    print("="*70)
    print()
    
    tables = ['fact_sales', 'dim_date', 'dim_product', 'dim_user', 'dim_rider']
    
    for table in tables:
        print(f"Analyzing {table}...")
        try:
            with engine.connect() as conn:
                with conn.begin():
                    conn.execute(text(f"ANALYZE TABLE {table};"))
            print(f"  ✅ Complete")
        except Exception as e:
            print(f"  ❌ Failed: {e}")
        print()
    
    print("="*70)
    print("✅ Statistics update complete")
    print("="*70)


def main():
    """Main function"""
    print()
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "INDEX CREATION SCRIPT" + " "*27 + "║")
    print("╚" + "="*68 + "╝")
    print()
    
    print("⚠️  WARNING: This script will create indexes in your database")
    print("   Make sure you have a backup before proceeding!")
    print()
    
    response = input("Do you want to continue? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("❌ Aborted by user")
        return
    
    print()
    
    # Create indexes
    create_indexes()
    
    print()
    response = input("Do you want to run ANALYZE TABLE now? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        print()
        analyze_tables()
    else:
        print("⏭️  Skipped ANALYZE TABLE - Remember to run it manually later!")
    
    print()
    print("="*70)
    print("🎉 Index creation process complete!")
    print("="*70)


if __name__ == "__main__":
    main()
