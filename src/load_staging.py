import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# =========================================
# Database Connection
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
    # Clear existing staging data
    # =========================================

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
    # File paths
    # =========================================

    customers_file = "data/large/customers.csv"
    products_file = "data/large/products.csv"
    orders_file = "data/large/orders.csv"
    order_items_file = "data/large/order_items.csv"


    # =========================================
    # Bulk Load Customers
    # =========================================

    with open(customers_file, "r") as file:
        cursor.copy_expert(
            """
            COPY staging_customers
            FROM STDIN
            WITH CSV HEADER
            """,
            file
        )

    print("Customers loaded.")


    # =========================================
    # Bulk Load Products
    # =========================================

    with open(products_file, "r") as file:
        cursor.copy_expert(
            """
            COPY staging_products
            FROM STDIN
            WITH CSV HEADER
            """,
            file
        )

    print("Products loaded.")


    # =========================================
    # Bulk Load Orders
    # =========================================

    with open(orders_file, "r") as file:
        cursor.copy_expert(
            """
            COPY staging_orders
            FROM STDIN
            WITH CSV HEADER
            """,
            file
        )

    print("Orders loaded.")


    # =========================================
    # Bulk Load Order Items
    # =========================================

    with open(order_items_file, "r") as file:
        cursor.copy_expert(
            """
            COPY staging_order_items
            FROM STDIN
            WITH CSV HEADER
            """,
            file
        )

    print("Order items loaded.")


    # =========================================
    # Commit
    # =========================================

    conn.commit()

    print("\n========================================")
    print("BULK LOAD COMPLETED SUCCESSFULLY")
    print("========================================")


    # =========================================
    # Verify Row Counts
    # =========================================

    cursor.execute(
        "SELECT COUNT(*) FROM staging_customers"
    )
    customers_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM staging_products"
    )
    products_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM staging_orders"
    )
    orders_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM staging_order_items"
    )
    order_items_count = cursor.fetchone()[0]


    print("\nStaging Row Counts")
    print("-------------------------")
    print(f"Customers   : {customers_count}")
    print(f"Products    : {products_count}")
    print(f"Orders      : {orders_count}")
    print(f"Order Items : {order_items_count}")


except Exception as error:

    conn.rollback()

    print("\nBULK LOAD FAILED")
    print("Error:", error)


finally:

    cursor.close()
    conn.close()

    print("\nDatabase connection closed.")