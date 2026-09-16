import os
from pathlib import Path

import pandas as pd
import psycopg2
import pyarrow as pa
import pyarrow.parquet as pq
from dotenv import load_dotenv


# =========================================
# 1. Project Paths
# =========================================

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "data_lake" / "sales"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================
# 2. Load Environment Variables
# =========================================

load_dotenv(BASE_DIR / ".env")


# =========================================
# 3. Connect to PostgreSQL
# =========================================

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

print("Connected to PostgreSQL successfully!")


try:

    # =========================================
    # 4. Read Fact Sales
    # =========================================

    query = """
        SELECT
            f.sales_key,
            f.order_id,
            f.customer_key,
            f.product_key,
            f.date_key,
            d.full_date,
            f.quantity,
            f.unit_price,
            f.total_amount
        FROM fact_sales f
        JOIN dim_date d
            ON f.date_key = d.date_key
        ORDER BY d.full_date;
    """

    print("Reading fact_sales...")

    df = pd.read_sql(query, conn)

    print(f"Records read: {len(df)}")


    # =========================================
    # 5. Create Partition Columns
    # =========================================

    df["full_date"] = pd.to_datetime(
        df["full_date"]
    )

    df["year"] = df["full_date"].dt.year

    df["month"] = df["full_date"].dt.month


    # =========================================
    # 6. Write Partitioned Parquet
    # =========================================

    print("\nWriting partitioned Parquet files...")

    table = pa.Table.from_pandas(
        df,
        preserve_index=False
    )

    pq.write_to_dataset(
        table,
        root_path=str(OUTPUT_DIR),
        partition_cols=["year", "month"]
    )


    # =========================================
    # 7. Report Partitions
    # =========================================

    print("\n========================================")
    print("PARQUET DATA LAKE CREATED")
    print("========================================")

    print(f"Total records : {len(df)}")
    print(f"Output path   : {OUTPUT_DIR}")

    partition_count = 0

    for path in OUTPUT_DIR.rglob("*.parquet"):

        partition_count += 1

    print(f"Parquet files : {partition_count}")


    # =========================================
    # 8. Display Sample
    # =========================================

    print("\nSample records:")

    print(
        df[
            [
                "order_id",
                "full_date",
                "quantity",
                "unit_price",
                "total_amount"
            ]
        ].head()
    )


    print("\n========================================")
    print("EXPORT COMPLETED SUCCESSFULLY")
    print("========================================")


except Exception as error:

    print("\n========================================")
    print("PARQUET EXPORT FAILED")
    print("========================================")

    print("Error:", error)


finally:

    conn.close()

    print("\nDatabase connection closed.")