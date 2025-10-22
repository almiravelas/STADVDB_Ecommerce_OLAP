import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy import text


def test_dashboard_kpi_aggregations(sqlite_engine: Engine):
    """Test dashboard KPI calculations - total orders, total sales, avg order value."""
    print("\n" + "="*80)
    print("OLAP TEST: Dashboard KPI Aggregations")
    print("="*80)
    
    print("\n📥 QUERY PURPOSE:")
    print("   Calculate key performance indicators for dashboard overview")
    
    print("\n📥 SEED DATA:")
    with sqlite_engine.connect() as conn:
        print("\nAll orders and sales:")
        sales = pd.read_sql(text("""
            SELECT order_number, sales_amount, customer_key, rider_key, product_key
            FROM fact_sales
        """), conn)
        print(sales.to_string(index=False))
    
    # Simulate dashboard KPI queries
    with sqlite_engine.connect() as conn:
        # Total distinct orders
        total_orders = pd.read_sql(text("""
            SELECT COUNT(DISTINCT order_number) as total_orders
            FROM fact_sales
        """), conn)
        
        # Total sales amount
        total_sales = pd.read_sql(text("""
            SELECT SUM(sales_amount) as total_sales
            FROM fact_sales
        """), conn)
        
        # Average order value
        avg_order = pd.read_sql(text("""
            SELECT AVG(order_total) as avg_order_value
            FROM (
                SELECT order_number, SUM(sales_amount) as order_total
                FROM fact_sales
                GROUP BY order_number
            ) order_totals
        """), conn)
        
        # Total customers
        total_customers = pd.read_sql(text("""
            SELECT COUNT(DISTINCT customer_key) as total_customers
            FROM fact_sales
        """), conn)
        
        # Total riders
        total_riders = pd.read_sql(text("""
            SELECT COUNT(DISTINCT rider_key) as total_riders
            FROM fact_sales
        """), conn)
        
        # Total products sold
        total_products = pd.read_sql(text("""
            SELECT COUNT(DISTINCT product_key) as total_products
            FROM fact_sales
        """), conn)
    
    print("\n📤 DASHBOARD KPIs:")
    print(f"   Total Orders: {total_orders['total_orders'].iloc[0]}")
    print(f"   Total Sales: ${total_sales['total_sales'].iloc[0]:,.2f}")
    print(f"   Average Order Value: ${avg_order['avg_order_value'].iloc[0]:,.2f}")
    print(f"   Total Customers: {total_customers['total_customers'].iloc[0]}")
    print(f"   Total Riders: {total_riders['total_riders'].iloc[0]}")
    print(f"   Total Products: {total_products['total_products'].iloc[0]}")
    
    print("\n✅ VALIDATION:")
    
    # Total orders: 4 distinct (ORD-1, ORD-2, ORD-3, ORD-4)
    assert total_orders['total_orders'].iloc[0] == 4
    print(f"   ✓ Total orders: 4 distinct orders")
    
    # Total sales: 100 + 250 + 300 + 400 = 1050
    assert total_sales['total_sales'].iloc[0] == 1050.0
    print(f"   ✓ Total sales: $1,050.00")
    
    # Average order value: 1050 / 4 = 262.5
    assert abs(avg_order['avg_order_value'].iloc[0] - 262.5) < 0.01
    print(f"   ✓ Average order value: ${avg_order['avg_order_value'].iloc[0]:.2f}")
    
    # Total customers: 3 (users 1, 2, 3)
    assert total_customers['total_customers'].iloc[0] == 3
    print(f"   ✓ Total customers: 3 users")
    
    # Total riders: 3 (riders 100, 101, 102)
    assert total_riders['total_riders'].iloc[0] == 3
    print(f"   ✓ Total riders: 3 delivery personnel")
    
    # Total products: 3 (products 10, 11, 12)
    assert total_products['total_products'].iloc[0] == 3
    print(f"   ✓ Total products sold: 3 SKUs")
    
    print("\n💡 USE CASE:")
    print("   These KPIs are displayed prominently on the dashboard")
    print("   Provide at-a-glance business health metrics")
    
    print("="*80 + "\n")


def test_dashboard_top_performers(sqlite_engine: Engine):
    """Test dashboard queries for top customers, riders, and products."""
    print("\n" + "="*80)
    print("OLAP TEST: Dashboard Top Performers")
    print("="*80)
    
    print("\n📥 QUERY PURPOSE:")
    print("   Identify top customers, riders, and products by sales volume")
    
    with sqlite_engine.connect() as conn:
        # Top customers
        top_customers = pd.read_sql(text("""
            SELECT 
                du.user_key,
                du.city,
                du.country,
                SUM(fs.sales_amount) as total_sales,
                COUNT(DISTINCT fs.order_number) as total_orders
            FROM fact_sales fs
            JOIN dim_user du ON fs.customer_key = du.user_key
            GROUP BY du.user_key, du.city, du.country
            ORDER BY total_sales DESC
            LIMIT 3
        """), conn)
        
        # Top riders
        top_riders = pd.read_sql(text("""
            SELECT 
                dr.rider_key,
                dr.rider_name,
                dr.courier_name,
                SUM(fs.sales_amount) as total_delivered,
                COUNT(DISTINCT fs.order_number) as total_deliveries
            FROM fact_sales fs
            JOIN dim_rider dr ON fs.rider_key = dr.rider_key
            GROUP BY dr.rider_key, dr.rider_name, dr.courier_name
            ORDER BY total_delivered DESC
            LIMIT 3
        """), conn)
        
        # Top products
        top_products = pd.read_sql(text("""
            SELECT 
                dp.product_key,
                dp.product_name,
                dp.category,
                SUM(fs.sales_amount) as total_revenue,
                SUM(fs.quantity) as units_sold
            FROM fact_sales fs
            JOIN dim_product dp ON fs.product_key = dp.product_key
            GROUP BY dp.product_key, dp.product_name, dp.category
            ORDER BY total_revenue DESC
            LIMIT 3
        """), conn)
    
    print("\n📤 TOP CUSTOMERS:")
    print(top_customers.to_string(index=False))
    
    print("\n📤 TOP RIDERS:")
    print(top_riders.to_string(index=False))
    
    print("\n📤 TOP PRODUCTS:")
    print(top_products.to_string(index=False))
    
    print("\n✅ VALIDATION:")
    
    # Top customer should be user 3 with 400
    assert top_customers.iloc[0]['user_key'] == 3
    assert top_customers.iloc[0]['total_sales'] == 400.0
    print(f"   ✓ Top customer: User {top_customers.iloc[0]['user_key']} with ${top_customers.iloc[0]['total_sales']}")
    
    # Top rider should be rider 100 with 500 (ORD-1: 100 + ORD-4: 400)
    assert top_riders.iloc[0]['rider_key'] == 100
    assert top_riders.iloc[0]['total_delivered'] == 500.0
    print(f"   ✓ Top rider: {top_riders.iloc[0]['rider_name']} with ${top_riders.iloc[0]['total_delivered']} delivered")
    
    # Top product by revenue
    top_prod = top_products.iloc[0]
    print(f"   ✓ Top product: {top_prod['product_name']} (${top_prod['total_revenue']} revenue)")
    
    print("\n💡 USE CASE:")
    print("   Dashboard highlights top performers for recognition and analysis")
    print("   Helps identify star customers, efficient riders, and best-selling products")
    
    print("="*80 + "\n")


def test_dashboard_monthly_trend(sqlite_engine: Engine):
    """Test dashboard monthly sales trend with multiple dimensions."""
    print("\n" + "="*80)
    print("OLAP TEST: Dashboard Monthly Trend (Multi-dimensional)")
    print("="*80)
    
    print("\n📥 QUERY PURPOSE:")
    print("   Monthly sales broken down by multiple dimensions for dashboard charts")
    
    with sqlite_engine.connect() as conn:
        # Monthly trend by category
        monthly_by_category = pd.read_sql(text("""
            SELECT 
                dd.year,
                dd.month,
                dd.month_name,
                dp.category,
                SUM(fs.sales_amount) as total_sales
            FROM fact_sales fs
            JOIN dim_date dd ON fs.date_key = dd.date_key
            JOIN dim_product dp ON fs.product_key = dp.product_key
            GROUP BY dd.year, dd.month, dd.month_name, dp.category
            ORDER BY dd.year, dd.month, dp.category
        """), conn)
        
        # Monthly trend by courier
        monthly_by_courier = pd.read_sql(text("""
            SELECT 
                dd.year,
                dd.month_name,
                dr.courier_name,
                SUM(fs.sales_amount) as total_sales,
                COUNT(DISTINCT fs.order_number) as orders_delivered
            FROM fact_sales fs
            JOIN dim_date dd ON fs.date_key = dd.date_key
            JOIN dim_rider dr ON fs.rider_key = dr.rider_key
            GROUP BY dd.year, dd.month_name, dr.courier_name
            ORDER BY dd.year, dd.month_name, total_sales DESC
        """), conn)
    
    print("\n📤 MONTHLY SALES BY CATEGORY:")
    print(monthly_by_category.to_string(index=False))
    print(f"\nShape: {monthly_by_category.shape}")
    
    print("\n📤 MONTHLY DELIVERIES BY COURIER:")
    print(monthly_by_courier.to_string(index=False))
    print(f"\nShape: {monthly_by_courier.shape}")
    
    print("\n✅ VALIDATION:")
    
    # Should have data for January and May
    months = set(monthly_by_category["month_name"])
    assert "January" in months and "May" in months
    print(f"   ✓ Months present: {months}")
    
    # Should have Electronics, Toys, Bags categories
    categories = set(monthly_by_category["category"])
    assert categories.issubset({"Electronics", "Toys", "Bags"})
    print(f"   ✓ Categories present: {categories}")
    
    # Should have FEDEX, DHL, UPS couriers
    couriers = set(monthly_by_courier["courier_name"])
    assert couriers.issubset({"FEDEX", "DHL", "UPS"})
    print(f"   ✓ Couriers present: {couriers}")
    
    # Validate totals
    total_by_cat = monthly_by_category["total_sales"].sum()
    total_by_courier = monthly_by_courier["total_sales"].sum()
    assert total_by_cat == 1050.0, f"Category total incorrect: {total_by_cat}"
    assert total_by_courier == 1050.0, f"Courier total incorrect: {total_by_courier}"
    print(f"   ✓ Total sales consistent across dimensions: ${total_by_cat}")
    
    print("\n💡 USE CASE:")
    print("   Dashboard displays multi-dimensional trends in interactive charts")
    print("   Allows users to see how sales vary by time AND another dimension")
    
    print("="*80 + "\n")
