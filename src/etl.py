import os
import pandas as pd
import psycopg2
import pyarrow as pa
import pyarrow.parquet as pq
from dotenv import load_dotenv

load_dotenv()
# =========================================
# 1. Database Connection
# =========================================

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

cursor = conn.cursor()

print("Connected to PostgreSQL successfully!")


try:

    # =========================================
    # 2. Extract - Read CSV Files
    # =========================================

    customers = pd.read_csv("data/customers.csv")
    products = pd.read_csv("data/products.csv")
    orders = pd.read_csv("data/orders.csv")
    order_items = pd.read_csv("data/order_items.csv")

    print("CSV files loaded successfully!")


    # =========================================
    # 3. Load Raw Customers
    # =========================================

    for _, row in customers.iterrows():

        cursor.execute(
            """
            INSERT INTO customers
            (customer_id, customer_name, city, state)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (customer_id) DO NOTHING
            """,
            (
                row["customer_id"],
                row["customer_name"],
                row["city"],
                row["state"]
            )
        )


    # =========================================
    # 4. Load Raw Products
    # =========================================

    for _, row in products.iterrows():

        cursor.execute(
            """
            INSERT INTO products
            (product_id, product_name, category, price)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (product_id) DO NOTHING
            """,
            (
                row["product_id"],
                row["product_name"],
                row["category"],
                row["price"]
            )
        )


    # =========================================
    # 5. Load Raw Orders
    # =========================================

    for _, row in orders.iterrows():

        cursor.execute(
            """
            INSERT INTO orders
            (order_id, customer_id, order_date)
            VALUES (%s, %s, %s)
            ON CONFLICT (order_id) DO NOTHING
            """,
            (
                row["order_id"],
                row["customer_id"],
                row["order_date"]
            )
        )


    # =========================================
    # 6. Load Raw Order Items
    # =========================================

    for _, row in order_items.iterrows():

        cursor.execute(
            """
            INSERT INTO order_items
            (order_item_id, order_id, product_id, quantity)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (order_item_id) DO NOTHING
            """,
            (
                row["order_item_id"],
                row["order_id"],
                row["product_id"],
                row["quantity"]
            )
        )


    conn.commit()

    print("Raw data loaded successfully!")


    # =========================================
    # 7. Data Quality Checks
    # =========================================

    cursor.execute("SELECT COUNT(*) FROM customers")
    customer_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders")
    order_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM order_items")
    order_item_count = cursor.fetchone()[0]


    print("\nData Quality Report")
    print("-------------------")
    print(f"Customers   : {customer_count}")
    print(f"Products    : {product_count}")
    print(f"Orders      : {order_count}")
    print(f"Order Items : {order_item_count}")


    if customer_count == 10:
        print("✓ Customer validation passed")
    else:
        print("✗ Customer validation failed")


    if product_count == 10:
        print("✓ Product validation passed")
    else:
        print("✗ Product validation failed")


    if order_count == 12:
        print("✓ Order validation passed")
    else:
        print("✗ Order validation failed")


    if order_item_count == 24:
        print("✓ Order item validation passed")
    else:
        print("✗ Order item validation failed")


    # =========================================
    # 8. Populate Customer Dimension
    # =========================================

    cursor.execute(
        """
        INSERT INTO dim_customer (
            customer_id,
            customer_name,
            city,
            state
        )
        SELECT
            customer_id,
            customer_name,
            city,
            state
        FROM customers
        WHERE customer_id NOT IN (
            SELECT customer_id
            FROM dim_customer
        );
        """
    )


    # =========================================
    # 9. Populate Product Dimension
    # =========================================

    cursor.execute(
        """
        INSERT INTO dim_product (
            product_id,
            product_name,
            category,
            price
        )
        SELECT
            product_id,
            product_name,
            category,
            price
        FROM products
        WHERE product_id NOT IN (
            SELECT product_id
            FROM dim_product
        );
        """
    )


    # =========================================
    # 10. Populate Date Dimension
    # =========================================

    cursor.execute(
        """
        INSERT INTO dim_date (
            date_key,
            full_date,
            day,
            month,
            month_name,
            quarter,
            year
        )
        SELECT DISTINCT
            CAST(TO_CHAR(order_date, 'YYYYMMDD') AS INT),
            order_date,
            EXTRACT(DAY FROM order_date)::INT,
            EXTRACT(MONTH FROM order_date)::INT,
            TO_CHAR(order_date, 'Month'),
            EXTRACT(QUARTER FROM order_date)::INT,
            EXTRACT(YEAR FROM order_date)::INT
        FROM orders
        WHERE CAST(TO_CHAR(order_date, 'YYYYMMDD') AS INT)
              NOT IN (
                  SELECT date_key
                  FROM dim_date
              );
        """
    )


    # =========================================
    # 11. Populate Sales Fact Table
    # =========================================

    cursor.execute(
        """
        INSERT INTO fact_sales (
            order_id,
            customer_key,
            product_key,
            date_key,
            quantity,
            unit_price,
            total_amount
        )
        SELECT
            o.order_id,
            c.customer_key,
            p.product_key,
            d.date_key,
            oi.quantity,
            p.price,
            oi.quantity * p.price
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        JOIN dim_customer c
            ON o.customer_id = c.customer_id
        JOIN dim_product p
            ON oi.product_id = p.product_id
        JOIN dim_date d
            ON o.order_date = d.full_date
        WHERE NOT EXISTS (
            SELECT 1
            FROM fact_sales f
            WHERE f.order_id = o.order_id
              AND f.product_key = p.product_key
        );
        """
    )


    conn.commit()

    print("\nData warehouse updated successfully!")


    # =========================================
    # 12. Export Fact Table to Parquet
    # =========================================

    query = """
    SELECT
        sales_key,
        order_id,
        customer_key,
        product_key,
        date_key,
        quantity,
        unit_price,
        total_amount
    FROM fact_sales
    """

    fact_sales = pd.read_sql(query, conn)

    table = pa.Table.from_pandas(fact_sales)

    pq.write_table(
        table,
        "output/fact_sales.parquet"
    )

    print("fact_sales exported to Parquet successfully!")


except Exception as error:

    conn.rollback()

    print("\nETL pipeline failed!")
    print("Error:", error)


finally:

    cursor.close()
    conn.close()

    print("Database connection closed.")
    print("ETL process completed!")