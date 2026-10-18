-- COUNT(DISTINCT order_id) karena setelah JOIN ke item, satu order jadi beberapa baris.
SELECT d.distributor_id, d.distributor_name,
       COUNT(DISTINCT o.order_id)    AS n_orders,
       ROUND(SUM(oi.line_amount), 2) AS revenue
FROM orders_clean o
JOIN distributors d       ON d.distributor_id = o.distributor_id
JOIN order_items_clean oi ON oi.order_id = o.order_id
WHERE o.status = 'COMPLETED'
  AND o.order_date >= DATE '2025-01-01' AND o.order_date < DATE '2026-01-01'
GROUP BY d.distributor_id, d.distributor_name
ORDER BY revenue DESC;
