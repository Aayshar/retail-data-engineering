# Databricks Data Engineering Pipeline

This project extends the retail data engineering pipeline using Databricks Free Edition.

## Architecture

CSV Files
   ↓
Bronze Layer
   ↓
Silver Layer
   ↓
Gold Layer
   ↓
Analytics & Visualizations

## Dataset

The pipeline processes:

- Customers: 10,000 records
- Products: 1,000 records
- Orders: 100,000 records
- Order Items: 250,213 records

## Bronze Layer

Raw CSV data is ingested into Delta tables:

- bronze_customers
- bronze_products
- bronze_orders
- bronze_order_items

## Silver Layer

Data is cleaned using:

- Duplicate removal
- Null-value handling
- Basic data validation

Silver tables:

- silver_customers
- silver_products
- silver_orders
- silver_order_items

## Gold Layer

The Gold layer provides analytics-ready tables:

- gold_fact_sales
- gold_dim_customer
- gold_dim_product
- gold_dim_date

The fact table contains 250,213 sales records.

## Analytics

The pipeline supports:

- Total sales and orders
- Monthly sales trends
- Top 10 products
- Sales by state
- Sales by product category

## Technologies

- Python
- PySpark
- SQL
- Databricks Free Edition
- Delta Lake
- PostgreSQL
- Git/GitHub

## Data Engineering Concepts Demonstrated

- ETL
- Medallion Architecture
- Data Cleaning
- Star Schema
- Dimensional Modeling
- Distributed Data Processing with Spark
- SQL Analytics
- Data Visualization