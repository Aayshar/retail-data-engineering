-- =========================================
-- Incremental ETL Transformation
-- =========================================


-- =========================================
-- 1. Get last processed order
-- =========================================

DO $$
DECLARE
    last_order_number INT;
BEGIN

    SELECT COALESCE(
        (
            SELECT last_processed_order_id
            FROM etl_metadata
            WHERE pipeline_name = 'retail_sales'
        ),
        0
    )
    INTO last_order_number;


    -- =========================================
    -- 2. Load new customers
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
    -- 3. Load new products
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
    -- 4. Load new dates
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
        TO_CHAR(s.order_date, 'YYYYMMDD')::INT,
        s.order_date,
        EXTRACT(DAY FROM s.order_date)::INT,
        EXTRACT(MONTH FROM s.order_date)::INT,
        TRIM(TO_CHAR(s.order_date, 'Month')),
        EXTRACT(QUARTER FROM s.order_date)::INT,
        EXTRACT(YEAR FROM s.order_date)::INT
    FROM staging_orders s
    WHERE NOT EXISTS (
        SELECT 1
        FROM dim_date d
        WHERE d.full_date = s.order_date
    );


    -- =========================================
    -- 5. Insert only NEW sales
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
        p.price,
        oi.quantity * p.price
    FROM staging_orders o

    JOIN staging_order_items oi
        ON o.order_id = oi.order_id

    JOIN dim_customer c
        ON o.customer_id = c.customer_id

    JOIN dim_product p
        ON oi.product_id = p.product_id

    JOIN dim_date d
        ON o.order_date = d.full_date

    WHERE
        CAST(SUBSTRING(o.order_id FROM 2) AS INT)
        > last_order_number

        AND NOT EXISTS (
            SELECT 1
            FROM fact_sales f
            WHERE f.order_id = o.order_id
              AND f.product_key = p.product_key
        );


    -- =========================================
    -- 6. Update metadata
    -- =========================================

    INSERT INTO etl_metadata (
        pipeline_name,
        last_processed_order_id,
        last_processed_date,
        last_run_timestamp,
        status
    )
    SELECT
        'retail_sales',
        MAX(
            CAST(SUBSTRING(order_id FROM 2) AS INT)
        ),
        MAX(order_date),
        CURRENT_TIMESTAMP,
        'SUCCESS'
    FROM staging_orders

    ON CONFLICT (pipeline_name)
    DO UPDATE SET
        last_processed_order_id =
            EXCLUDED.last_processed_order_id,
        last_processed_date =
            EXCLUDED.last_processed_date,
        last_run_timestamp =
            EXCLUDED.last_run_timestamp,
        status =
            EXCLUDED.status;

END $$;


-- =========================================
-- 7. Show ETL Metadata
-- =========================================

SELECT *
FROM etl_metadata
WHERE pipeline_name = 'retail_sales';