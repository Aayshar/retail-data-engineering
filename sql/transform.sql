-- =========================================
-- Staging → Data Warehouse Transformation
-- =========================================


-- =========================================
-- 1. Load Customer Dimension
-- =========================================

INSERT INTO dim_customer (
    customer_id,
    customer_name,
    city,
    state
)
SELECT
    s.customer_id,
    s.customer_name,
    s.city,
    s.state
FROM staging_customers s
WHERE NOT EXISTS (
    SELECT 1
    FROM dim_customer d
    WHERE d.customer_id = s.customer_id
);


-- =========================================
-- 2. Load Product Dimension
-- =========================================

INSERT INTO dim_product (
    product_id,
    product_name,
    category,
    price
)
SELECT
    s.product_id,
    s.product_name,
    s.category,
    s.price
FROM staging_products s
WHERE NOT EXISTS (
    SELECT 1
    FROM dim_product d
    WHERE d.product_id = s.product_id
);


-- =========================================
-- 3. Load Date Dimension
-- =========================================

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
    TO_CHAR(order_date, 'YYYYMMDD')::INT AS date_key,
    order_date,
    EXTRACT(DAY FROM order_date)::INT,
    EXTRACT(MONTH FROM order_date)::INT,
    TRIM(TO_CHAR(order_date, 'Month')),
    EXTRACT(QUARTER FROM order_date)::INT,
    EXTRACT(YEAR FROM order_date)::INT
FROM staging_orders s
WHERE NOT EXISTS (
    SELECT 1
    FROM dim_date d
    WHERE d.full_date = s.order_date
);


-- =========================================
-- 4. Load Sales Fact
-- =========================================

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
    p.price AS unit_price,
    oi.quantity * p.price AS total_amount
FROM staging_orders o

JOIN staging_order_items oi
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


-- =========================================
-- 5. Transformation Summary
-- =========================================

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