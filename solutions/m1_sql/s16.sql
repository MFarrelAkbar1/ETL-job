WITH daily AS (
    SELECT d.region_id, o.order_date, SUM(oi.line_amount) AS daily_revenue
    FROM orders_clean o
    JOIN distributors d ON d.distributor_id = o.distributor_id
    JOIN order_items_clean oi ON oi.order_id = o.order_id
    WHERE o.status = 'COMPLETED'
    GROUP BY 1, 2
)
SELECT region_id, order_date,
       ROUND(daily_revenue, 2) AS daily_revenue,
       ROUND(SUM(daily_revenue) OVER (
           PARTITION BY region_id, year(order_date)
           ORDER BY order_date
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS running_revenue
FROM daily
ORDER BY region_id, order_date;
