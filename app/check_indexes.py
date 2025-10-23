"""
Helper script to check existing indexes in the database
"""
from utils.db_connection import get_warehouse_engine
from sqlalchemy import text
import pandas as pd


def check_indexes():
    """Check what indexes currently exist in the database"""
    engine = get_warehouse_engine()
    
    if engine is None:
        print("❌ Failed to connect to database")
        return
    
    print("🔍 Checking existing indexes...\n")
    
    # Get list of tables
    tables = ['fact_sales', 'dim_date', 'dim_product', 'dim_user', 'dim_rider']
    
    for table in tables:
        print(f"\n{'='*60}")
        print(f"📊 Table: {table}")
        print('='*60)
        
        query = f"SHOW INDEX FROM {table};"
        
        try:
            with engine.connect() as conn:
                result = pd.read_sql(text(query), conn)
                
                if result.empty:
                    print("  No indexes found")
                else:
                    # Group by index name
                    for idx_name in result['Key_name'].unique():
                        idx_data = result[result['Key_name'] == idx_name]
                        columns = ', '.join(idx_data['Column_name'].tolist())
                        is_unique = 'UNIQUE' if idx_data['Non_unique'].iloc[0] == 0 else 'NON-UNIQUE'
                        index_type = idx_data['Index_type'].iloc[0]
                        
                        print(f"  ✓ {idx_name}")
                        print(f"    - Columns: {columns}")
                        print(f"    - Type: {index_type} ({is_unique})")
                        print()
                        
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n" + "="*60)
    print("✅ Index check complete")
    print("="*60)


if __name__ == "__main__":
    check_indexes()
