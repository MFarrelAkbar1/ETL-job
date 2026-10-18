WITH spine AS (
    SELECT CAST(d AS DATE) AS order_date
    FROM generate_series(DATE '2025-01-01', DATE '2025-03-31', INTERVAL 1 DAY) t(d)
),
daily AS (
    SELECT o.order_date, SUM(oi.line_amount) AS revenue
    FROM orders_clean o
    JOIN order_items_clean oi ON oi.order_id = o.order_id
    WHERE o.status = 'COMPLETED' AND o.distributor_id = 'D007'
      AND o.order_date BETWEEN DATE '2025-01-01' AND DATE '2025-03-31'
    GROUP BY 1
),
filled AS (
    SELECT s.order_date, COALESCE(d.revenue, 0) AS daily_revenue
    FROM spine s LEFT JOIN daily d USING (order_date)
)
SELECT order_date,
       ROUND(daily_revenue, 2) AS daily_revenue,
       ROUND(AVG(daily_revenue) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS ma_7d
FROM filled
ORDER BY order_date;
