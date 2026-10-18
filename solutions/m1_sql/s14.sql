WITH monthly AS (
    SELECT p.segment, DATE_TRUNC('month', o.order_date)::DATE AS month, SUM(oi.line_amount) AS revenue
    FROM orders_clean o
    JOIN order_items_clean oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_code = oi.product_code
    WHERE o.status = 'COMPLETED'
    GROUP BY 1, 2
)
SELECT segment, month,
       ROUND(revenue, 2) AS revenue,
       ROUND(LAG(revenue) OVER w, 2) AS prev_revenue,
       ROUND((revenue - LAG(revenue) OVER w) / LAG(revenue) OVER w * 100, 2) AS mom_pct
FROM monthly
WINDOW w AS (PARTITION BY segment ORDER BY month)
ORDER BY segment, month;
