SELECT p.category,
       ROUND(COALESCE(SUM(oi.line_amount) FILTER (WHERE quarter(o.order_date) = 1), 0), 2) AS q1,
       ROUND(COALESCE(SUM(oi.line_amount) FILTER (WHERE quarter(o.order_date) = 2), 0), 2) AS q2,
       ROUND(COALESCE(SUM(oi.line_amount) FILTER (WHERE quarter(o.order_date) = 3), 0), 2) AS q3,
       ROUND(COALESCE(SUM(oi.line_amount) FILTER (WHERE quarter(o.order_date) = 4), 0), 2) AS q4,
       ROUND(SUM(oi.line_amount), 2) AS total
FROM orders_clean o
JOIN order_items_clean oi ON oi.order_id = o.order_id
JOIN products p ON p.product_code = oi.product_code
WHERE o.status = 'COMPLETED'
  AND o.order_date >= DATE '2025-01-01' AND o.order_date < DATE '2026-01-01'
GROUP BY p.category
ORDER BY total DESC;
