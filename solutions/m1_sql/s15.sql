WITH days AS (
    SELECT DISTINCT o.distributor_id, o.order_date
    FROM orders_clean o
    JOIN distributors d ON d.distributor_id = o.distributor_id
    WHERE o.order_date >= DATE '2025-01-01' AND o.order_date < DATE '2026-01-01'
),
nxt AS (
    SELECT distributor_id, order_date,
           LEAD(order_date) OVER (PARTITION BY distributor_id ORDER BY order_date) AS next_order_date
    FROM days
)
SELECT distributor_id, order_date, next_order_date,
       CAST(next_order_date - order_date AS INTEGER) AS gap_days
FROM nxt
WHERE next_order_date - order_date >= 21
ORDER BY distributor_id, order_date;
