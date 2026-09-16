import os
import time
from pathlib import Path
from datetime import datetime

import psycopg2
from dotenv import load_dotenv


# =========================================
# 1. Project Paths
# =========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "large"
SQL_DIR = BASE_DIR / "sql"

CUSTOMERS_FILE = DATA_DIR / "customers.csv"
PRODUCTS_FILE = DATA_DIR / "products.csv"
ORDERS_FILE = DATA_DIR / "orders.csv"
ORDER_ITEMS_FILE = DATA_DIR / "order_items.csv"

INCREMENTAL_SQL_FILE = SQL_DIR / "incremental_transform.sql"


# =========================================
# 2. Load Environment Variables
# =========================================

load_dotenv(BASE_DIR / ".env")


# =========================================
# 3. Start Monitoring
# =========================================

pipeline_name = "retail_sales_incremental"

start_time = datetime.now()

timer_start = time.perf_counter()

status = "SUCCESS"
error_message = None
rows_processed = 0


# =========================================
# 4. Database Connection
# =========================================

conn = None
cursor = None

try:

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

    cursor = conn.cursor()

    print("========================================")
    print("INCREMENTAL ETL PIPELINE")
    print("========================================")

    print("Connected to PostgreSQL successfully!")


    # =========================================
    # 5. Clear Staging Tables
    # =========================================

    print("\nPreparing staging tables...")

    cursor.execute("""
        TRUNCATE TABLE
            staging_order_items,
            staging_orders,
            staging_products,
            staging_customers;
    """)

    conn.commit()

    print("Staging tables cleared.")


    # =========================================
    # 6. Bulk Load Customers
    # =========================================

    print("\nLoading customers...")

    with open(CUSTOMERS_FILE, "r") as file:

        cursor.copy_expert(
            """
            COPY staging_customers
            (
                customer_id,
                customer_name,
                city,
                state
            )
            FROM STDIN
            WITH CSV HEADER
            """,
            file
        )

    print("Customers loaded.")


    # =========================================
    # 7. Bulk Load Products
    # =========================================

    print("Loading products...")

    with open(PRODUCTS_FILE, "r") as file:

        cursor.copy_expert(
            """
            COPY staging_products
            (
                product_id,
                product_name,
                category,
                price
            )
            FROM STDIN
            WITH CSV HEADER
            """,
            file
        )

    print("Products loaded.")


    # =========================================
    # 8. Bulk Load Orders
    # =========================================

    print("Loading orders...")

    with open(ORDERS_FILE, "r") as file:

        cursor.copy_expert(
            """
            COPY staging_orders
            (
                order_id,
                customer_id,
                order_date
            )
            FROM STDIN
            WITH CSV HEADER
            """,
            file
        )

    print("Orders loaded.")


    # =========================================
    # 9. Bulk Load Order Items
    # =========================================

    print("Loading order items...")

    with open(ORDER_ITEMS_FILE, "r") as file:

        cursor.copy_expert(
            """
            COPY staging_order_items
            (
                order_item_id,
                order_id,
                product_id,
                quantity
            )
            FROM STDIN
            WITH CSV HEADER
            """,
            file
        )

    conn.commit()

    print("Order items loaded.")


    # =========================================
    # 10. Count Staging Rows
    # =========================================

    print("\n========================================")
    print("STAGING DATA QUALITY")
    print("========================================")

    cursor.execute(
        "SELECT COUNT(*) FROM staging_customers"
    )
    customer_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM staging_products"
    )
    product_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM staging_orders"
    )
    order_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM staging_order_items"
    )
    order_item_count = cursor.fetchone()[0]

    print(f"Customers   : {customer_count}")
    print(f"Products    : {product_count}")
    print(f"Orders      : {order_count}")
    print(f"Order Items : {order_item_count}")


    # =========================================
    # 11. Calculate Processed Rows
    # =========================================

    rows_processed = order_item_count


    # =========================================
    # 12. Incremental Transformation
    # =========================================

    print("\nRunning incremental transformation...")

    with open(INCREMENTAL_SQL_FILE, "r") as file:

        incremental_sql = file.read()

    cursor.execute(incremental_sql)

    conn.commit()

    print("Incremental transformation completed.")


    # =========================================
    # 13. Get ETL Metadata
    # =========================================

    cursor.execute("""
        SELECT
            pipeline_name,
            last_processed_order_id,
            last_processed_date,
            last_run_timestamp,
            status
        FROM etl_metadata
        WHERE pipeline_name = 'retail_sales';
    """)

    metadata = cursor.fetchone()


    print("\n========================================")
    print("ETL METADATA")
    print("========================================")

    if metadata:

        print(f"Pipeline              : {metadata[0]}")
        print(f"Last Processed Order  : {metadata[1]}")
        print(f"Last Processed Date   : {metadata[2]}")
        print(f"Last Run              : {metadata[3]}")
        print(f"Status                : {metadata[4]}")

    else:

        print("No ETL metadata found.")


    # =========================================
    # 14. Warehouse Counts
    # =========================================

    print("\n========================================")
    print("WAREHOUSE COUNTS")
    print("========================================")

    cursor.execute("""
        SELECT
            'dim_customer' AS table_name,
            COUNT(*) AS row_count
        FROM dim_customer

        UNION ALL

        SELECT
            'dim_product',
            COUNT(*)
        FROM dim_product

        UNION ALL

        SELECT
            'dim_date',
            COUNT(*)
        FROM dim_date

        UNION ALL

        SELECT
            'fact_sales',
            COUNT(*)
        FROM fact_sales;
    """)

    results = cursor.fetchall()

    for table_name, row_count in results:

        print(
            f"{table_name:<15}: {row_count}"
        )


    # =========================================
    # 15. Successful Run
    # =========================================

    status = "SUCCESS"

    print("\n========================================")
    print("INCREMENTAL ETL COMPLETED SUCCESSFULLY")
    print("========================================")


except Exception as error:

    status = "FAILED"

    error_message = str(error)

    if conn:

        conn.rollback()

    print("\n========================================")
    print("ETL PIPELINE FAILED")
    print("========================================")

    print("Error:", error)


finally:

    # =========================================
    # 16. Calculate Runtime
    # =========================================

    timer_end = time.perf_counter()

    duration = timer_end - timer_start

    end_time = datetime.now()


    # =========================================
    # 17. Save Monitoring Record
    # =========================================

    if conn and cursor:

        try:

            cursor.execute(
                """
                INSERT INTO etl_runs
                (
                    pipeline_name,
                    start_time,
                    end_time,
                    duration_seconds,
                    status,
                    rows_processed,
                    error_message
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    pipeline_name,
                    start_time,
                    end_time,
                    duration,
                    status,
                    rows_processed,
                    error_message
                )
            )

            conn.commit()

            print("\nETL monitoring record saved.")

        except Exception as monitoring_error:

            print(
                "Could not save monitoring record:",
                monitoring_error
            )


    # =========================================
    # 18. Close Database
    # =========================================

    if cursor:

        cursor.close()

    if conn:

        conn.close()

    print(
        f"Pipeline duration: {duration:.2f} seconds"
    )

    print("Database connection closed.")