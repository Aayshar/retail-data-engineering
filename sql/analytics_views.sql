-- =========================================
-- Retail Sales Analytics Views
-- =========================================


-- =========================================
-- 1. Daily Sales View
-- =========================================

CREATE OR REPLACE VIEW vw_daily_sales AS

SELECT
    d.full_date,
    d.year,
    d.month,
    d.month_name,
    d.quarter,

    COUNT(DISTINCT f.order_id) AS total_orders,

    SUM(f.quantity) AS units_sold,

    SUM(f.total_amount) AS total_revenue

FROM fact_sales f

JOIN dim_date d
    ON f.date_key = d.date_key

GROUP BY
    d.full_date,
    d.year,
    d.month,
    d.month_name,
    d.quarter;


-- =========================================
-- 2. Product Sales View
-- =========================================

CREATE OR REPLACE VIEW vw_product_sales AS

SELECT
    p.product_id,
    p.product_name,
    p.category,

    SUM(f.quantity) AS units_sold,

    SUM(f.total_amount) AS total_revenue,

    COUNT(DISTINCT f.order_id) AS total_orders

FROM fact_sales f

JOIN dim_product p
    ON f.product_key = p.product_key

GROUP BY
    p.product_id,
    p.product_name,
    p.category;


-- =========================================
-- 3. Customer Sales View
-- =========================================

CREATE OR REPLACE VIEW vw_customer_sales AS

SELECT
    c.customer_id,
    c.customer_name,
    c.city,
    c.state,

    COUNT(DISTINCT f.order_id) AS total_orders,

    SUM(f.quantity) AS units_purchased,

    SUM(f.total_amount) AS total_spent

FROM fact_sales f

JOIN dim_customer c
    ON f.customer_key = c.customer_key

GROUP BY
    c.customer_id,
    c.customer_name,
    c.city,
    c.state;