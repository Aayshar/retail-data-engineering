import os
import time
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


# =========================================
# 1. Project Paths
# =========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "large"

CUSTOMERS_FILE = DATA_DIR / "customers.csv"


# =========================================
# 2. Load Environment Variables
# =========================================

load_dotenv(BASE_DIR / ".env")


# =========================================
# 3. Database Connection
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
    # 4. Clear Benchmark Table
    # =========================================

    cursor.execute("""
        DROP TABLE IF EXISTS benchmark_customers;
    """)

    cursor.execute("""
        CREATE TABLE benchmark_customers (
            customer_id VARCHAR(20),
            customer_name VARCHAR(100),
            city VARCHAR(100),
            state VARCHAR(100)
        );
    """)

    conn.commit()


    # =========================================
    # 5. Read CSV
    # =========================================

    with open(CUSTOMERS_FILE, "r") as file:
        lines = file.readlines()

    data_lines = lines[1:]


    # =========================================
    # 6. Row-by-Row INSERT
    # =========================================

    print("\n========================================")
    print("ROW-BY-ROW INSERT")
    print("========================================")

    start_time = time.perf_counter()

    for line in data_lines:

        values = line.strip().split(",")

        cursor.execute(
            """
            INSERT INTO benchmark_customers
            (
                customer_id,
                customer_name,
                city,
                state
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                values[0],
                values[1],
                values[2],
                values[3]
            )
        )

    conn.commit()

    row_insert_time = time.perf_counter() - start_time

    print(
        f"Row-by-row time: "
        f"{row_insert_time:.4f} seconds"
    )


    # =========================================
    # 7. Clear Table
    # =========================================

    cursor.execute(
        "TRUNCATE TABLE benchmark_customers"
    )

    conn.commit()


    # =========================================
    # 8. Bulk COPY
    # =========================================

    print("\n========================================")
    print("BULK COPY")
    print("========================================")

    start_time = time.perf_counter()

    with open(CUSTOMERS_FILE, "r") as file:

        cursor.copy_expert(
            """
            COPY benchmark_customers
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

    conn.commit()

    copy_time = time.perf_counter() - start_time

    print(
        f"Bulk COPY time: "
        f"{copy_time:.4f} seconds"
    )


    # =========================================
    # 9. Calculate Improvement
    # =========================================

    if copy_time > 0:

        speedup = row_insert_time / copy_time

        improvement = (
            (row_insert_time - copy_time)
            / row_insert_time
        ) * 100

        print("\n========================================")
        print("PERFORMANCE COMPARISON")
        print("========================================")

        print(
            f"Row-by-row : "
            f"{row_insert_time:.4f} sec"
        )

        print(
            f"Bulk COPY  : "
            f"{copy_time:.4f} sec"
        )

        print(
            f"Speedup     : "
            f"{speedup:.2f}x"
        )

        print(
            f"Improvement : "
            f"{improvement:.2f}%"
        )


    # =========================================
    # 10. Verify Row Count
    # =========================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM benchmark_customers;
    """)

    count = cursor.fetchone()[0]

    print("\nRows loaded:", count)

    print("\nBenchmark completed successfully!")


except Exception as error:

    conn.rollback()

    print("\nBenchmark failed!")
    print("Error:", error)


finally:

    cursor.close()
    conn.close()

    print("Database connection closed.")