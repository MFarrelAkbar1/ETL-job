SELECT order_id, order_date, distributor_id, status, channel, updated_at
FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) AS rn
    FROM orders
)
WHERE rn = 1
ORDER BY order_id;
-- Versi ringkas (DuckDB, Snowflake, Databricks):
-- SELECT * FROM orders QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) = 1
