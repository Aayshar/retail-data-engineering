-- =========================================
-- Retail Data Engineering - Staging Layer
-- =========================================

DROP TABLE IF EXISTS staging_order_items;
DROP TABLE IF EXISTS staging_orders;
DROP TABLE IF EXISTS staging_products;
DROP TABLE IF EXISTS staging_customers;


-- =========================================
-- Staging Customers
-- =========================================

CREATE TABLE staging_customers (
    customer_id VARCHAR(10),
    customer_name VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(50)
);


-- =========================================
-- Staging Products
-- =========================================

CREATE TABLE staging_products (
    product_id VARCHAR(10),
    product_name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10,2)
);


-- =========================================
-- Staging Orders
-- =========================================

CREATE TABLE staging_orders (
    order_id VARCHAR(10),
    customer_id VARCHAR(10),
    order_date DATE
);


-- =========================================
-- Staging Order Items
-- =========================================

CREATE TABLE staging_order_items (
    order_item_id INT,
    order_id VARCHAR(10),
    product_id VARCHAR(10),
    quantity INT
);