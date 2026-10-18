SELECT o.distributor_id,
       COUNT(DISTINCT o.order_id) AS n_orders,
       ROUND(COALESCE(SUM(oi.line_amount) FILTER (WHERE o.status = 'COMPLETED'), 0), 2) AS revenue
FROM orders_clean o
LEFT JOIN order_items_clean oi ON oi.order_id = o.order_id
WHERE o.distributor_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM distributors d WHERE d.distributor_id = o.distributor_id)
GROUP BY o.distributor_id
ORDER BY o.distributor_id;
