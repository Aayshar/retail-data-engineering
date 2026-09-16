# Retail Data Engineering & Analytics Pipeline

An end-to-end data engineering pipeline that ingests large-scale retail data, performs data-quality validation, loads data into PostgreSQL using bulk ingestion, transforms it into a dimensional data warehouse, supports incremental processing, and exports analytical data to a partitioned Parquet data lake.

## Project Overview

This project simulates a production-style retail data platform.

The pipeline processes:

- 10,000 customers
- 1,000 products
- 100,000 orders
- 250,000+ order items

The system demonstrates the complete flow from raw CSV data to an analytical warehouse and partitioned data lake.

## Architecture

```text
                    CSV DATA
                       |
                       v
              Python Data Ingestion
                       |
                       v
             PostgreSQL STAGING
                       |
                       v
              Data Quality Checks
                       |
                       v
             Incremental ETL
                       |
                       v
                STAR SCHEMA
              /      |       \
             /       |        \
            v        v         v
     dim_customer dim_product dim_date
             \       |        /
              \      |       /
               v     v      v
                  fact_sales
                       |
             +---------+---------+
             |                   |
             v                   v
       Analytics Views     Parquet Data Lake
                              |
                              v
                    Year / Month Partitions
```
