WITH rev AS (
    SELECT p.category, p.product_code, p.product_name, SUM(oi.line_amount) AS revenue
    FROM orders_clean o
    JOIN order_items_clean oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_code = oi.product_code
    WHERE o.status = 'COMPLETED'
      AND o.order_date >= DATE '2025-01-01' AND o.order_date < DATE '2026-01-01'
    GROUP BY ALL
),
ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) AS rank_in_category
    FROM rev
)
SELECT category, rank_in_category, product_code, product_name, ROUND(revenue, 2) AS revenue
FROM ranked
WHERE rank_in_category <= 3
ORDER BY category, rank_in_category;
