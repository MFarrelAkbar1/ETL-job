SELECT o.distributor_id,
       COUNT(DISTINCT o.order_id)    AS n_orders,
       ROUND(SUM(oi.line_amount), 2) AS revenue
FROM orders_clean o
JOIN order_items_clean oi ON oi.order_id = o.order_id
WHERE o.status = 'COMPLETED'
  AND o.distributor_id IS NOT NULL
  AND o.order_date >= DATE '2025-01-01' AND o.order_date < DATE '2026-01-01'
GROUP BY o.distributor_id
HAVING SUM(oi.line_amount) >= 1500000000 AND COUNT(DISTINCT o.order_id) >= 300
ORDER BY revenue DESC;
