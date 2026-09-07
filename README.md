# Retail Data Engineering & Analytics Pipeline

## 📌 Project Overview

A data engineering pipeline that ingests retail data from CSV files, processes the data using Python, loads it into PostgreSQL, transforms it into a dimensional data warehouse, and exports analytical data to Parquet format.

The project demonstrates an end-to-end ETL workflow using Python, SQL, PostgreSQL, Pandas, and PyArrow.

---

## 🏗️ Architecture

CSV Files
↓
Python ETL Pipeline
↓
Data Validation
↓
PostgreSQL Raw Tables
↓
SQL Transformations
↓
Star Schema Data Warehouse
↓
Parquet
↓
SQL Analytics

## 🛠️ Technologies Used

- Python
- Pandas
- PostgreSQL
- SQL
- PyArrow
- Parquet
- Git & GitHub

## 📂 Data Sources

The pipeline processes four CSV files:

- customers.csv
- products.csv
- orders.csv
- order_items.csv

## 🔄 ETL Process

### 1. Extract

Python and Pandas read the raw retail data from CSV files.

### 2. Transform

SQL JOINs are used to combine orders, order items, customers, products, and dates.

Sales revenue is calculated using:

`total_amount = quantity × unit_price`

### 3. Load

The processed data is loaded into PostgreSQL.

The warehouse follows a Star Schema consisting of:

- dim_customer
- dim_product
- dim_date
- fact_sales

## ✅ Data Quality

The pipeline performs validation checks on:

- Customer record count
- Product record count
- Order record count
- Order item record count

Expected records:

| Dataset     | Records |
| ----------- | ------: |
| Customers   |      10 |
| Products    |      10 |
| Orders      |      12 |
| Order Items |      24 |
| Fact Sales  |      24 |

## 📊 Analytics

SQL queries are used to generate:

- Total revenue
- Revenue by product
- Revenue by category
- Revenue by customer
- Daily revenue

## 📁 Project Structure

retail-data-engineering/
│
├── data/
│ ├── customers.csv
│ ├── products.csv
│ ├── orders.csv
│ └── order_items.csv
│
├── src/
│ └── etl.py
│
├── sql/
│ ├── warehouse.sql
│ └── analytics.sql
│
├── output/
│ └── fact_sales.parquet
│
└── README.md

## 🎯 Key Learning Outcomes

- Built an end-to-end ETL pipeline
- Implemented data ingestion using Python
- Worked with PostgreSQL for data storage
- Used SQL JOINs and transformations
- Designed a Star Schema data warehouse
- Implemented basic data-quality validation
- Exported analytical data to Parquet
- Created SQL-based business analytics
