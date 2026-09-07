-- =========================================
-- Retail Data Engineering - Analytics
-- =========================================


-- 1. Total Revenue
SELECT
    SUM(total_amount) AS total_revenue
FROM fact_sales;


-- 2. Revenue by Product
SELECT
    p.product_name,
    SUM(f.quantity) AS total_quantity_sold,
    SUM(f.total_amount) AS total_revenue
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY p.product_name
ORDER BY total_revenue DESC;


-- 3. Revenue by Category
SELECT
    p.category,
    SUM(f.quantity) AS total_quantity_sold,
    SUM(f.total_amount) AS total_revenue
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY total_revenue DESC;


-- 4. Revenue by Customer
SELECT
    c.customer_name,
    c.city,
    c.state,
    SUM(f.total_amount) AS total_revenue
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_key = c.customer_key
GROUP BY
    c.customer_name,
    c.city,
    c.state
ORDER BY total_revenue DESC;


-- 5. Daily Revenue
SELECT
    d.full_date,
    SUM(f.total_amount) AS daily_revenue
FROM fact_sales f
JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY d.full_date
ORDER BY d.full_date;