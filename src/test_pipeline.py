import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


# =========================================
# 1. Project Configuration
# =========================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# =========================================
# 2. Database Connection
# =========================================

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

cursor = conn.cursor()

print("========================================")
print("DATA QUALITY TEST SUITE")
print("========================================")

print("Connected to PostgreSQL successfully!\n")

passed = 0
failed = 0


def run_test(test_name, query, expected=0):
    global passed, failed

    cursor.execute(query)

    result = cursor.fetchone()[0]

    if result == expected:
        print(f"✓ PASS: {test_name}")
        passed += 1
    else:
        print(f"✗ FAIL: {test_name} -> {result}")
        failed += 1


try:

    # =========================================
    # 3. Duplicate Customer IDs
    # =========================================

    run_test(
        "No duplicate customer IDs",
        """
        SELECT COUNT(*)
        FROM (
            SELECT customer_id
            FROM staging_customers
            GROUP BY customer_id
            HAVING COUNT(*) > 1
        ) duplicates;
        """
    )


    # =========================================
    # 4. Duplicate Product IDs
    # =========================================

    run_test(
        "No duplicate product IDs",
        """
        SELECT COUNT(*)
        FROM (
            SELECT product_id
            FROM staging_products
            GROUP BY product_id
            HAVING COUNT(*) > 1
        ) duplicates;
        """
    )


    # =========================================
    # 5. Duplicate Order IDs
    # =========================================

    run_test(
        "No duplicate order IDs",
        """
        SELECT COUNT(*)
        FROM (
            SELECT order_id
            FROM staging_orders
            GROUP BY order_id
            HAVING COUNT(*) > 1
        ) duplicates;
        """
    )


    # =========================================
    # 6. Invalid Customer References
    # =========================================

    run_test(
        "No invalid customer references",
        """
        SELECT COUNT(*)
        FROM staging_orders o
        LEFT JOIN staging_customers c
            ON o.customer_id = c.customer_id
        WHERE c.customer_id IS NULL;
        """
    )


    # =========================================
    # 7. Invalid Product References
    # =========================================

    run_test(
        "No invalid product references",
        """
        SELECT COUNT(*)
        FROM staging_order_items oi
        LEFT JOIN staging_products p
            ON oi.product_id = p.product_id
        WHERE p.product_id IS NULL;
        """
    )


    # =========================================
    # 8. Invalid Order References
    # =========================================

    run_test(
        "No invalid order references",
        """
        SELECT COUNT(*)
        FROM staging_order_items oi
        LEFT JOIN staging_orders o
            ON oi.order_id = o.order_id
        WHERE o.order_id IS NULL;
        """
    )


    # =========================================
    # 9. Negative Quantities
    # =========================================

    run_test(
        "No negative quantities",
        """
        SELECT COUNT(*)
        FROM staging_order_items
        WHERE quantity <= 0;
        """
    )


    # =========================================
    # 10. Invalid Product Prices
    # =========================================

    run_test(
        "No invalid product prices",
        """
        SELECT COUNT(*)
        FROM staging_products
        WHERE price <= 0;
        """
    )


    # =========================================
    # 11. NULL Customer IDs
    # =========================================

    run_test(
        "No NULL customer IDs",
        """
        SELECT COUNT(*)
        FROM staging_customers
        WHERE customer_id IS NULL;
        """
    )


    # =========================================
    # 12. NULL Product IDs
    # =========================================

    run_test(
        "No NULL product IDs",
        """
        SELECT COUNT(*)
        FROM staging_products
        WHERE product_id IS NULL;
        """
    )


    # =========================================
    # 13. Fact Table Check
    # =========================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM fact_sales;
    """)

    fact_count = cursor.fetchone()[0]

    if fact_count > 0:

        print(
            f"✓ PASS: Fact table contains "
            f"{fact_count} records"
        )

        passed += 1

    else:

        print("✗ FAIL: Fact table is empty")

        failed += 1


    # =========================================
    # 14. Test Summary
    # =========================================

    print("\n========================================")
    print("TEST SUMMARY")
    print("========================================")

    print(f"Tests Passed : {passed}")
    print(f"Tests Failed : {failed}")

    if failed == 0:

        print("\n✓ ALL DATA QUALITY TESTS PASSED")

    else:

        print("\n✗ DATA QUALITY TESTS FAILED")


except Exception as error:

    print("\nTest suite failed with error:")
    print(error)


finally:

    cursor.close()
    conn.close()

    print("\nDatabase connection closed.")