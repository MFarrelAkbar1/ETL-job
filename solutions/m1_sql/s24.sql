-- GROUP BY biasa menggantikan DISTINCT + window. Filter rentang tanggal langsung pada kolom
-- (sargable), sehingga min/max statistics atau partition pruning bisa dipakai.
SELECT r.region_name, p.segment, strftime(o.order_date, '%Y-%m') AS month,
       SUM(oi.line_amount) AS revenue
FROM orders_clean o
JOIN order_items_clean oi ON oi.order_id = o.order_id
JOIN products p     ON p.product_code = oi.product_code
JOIN distributors d ON d.distributor_id = o.distributor_id
JOIN regions r      ON r.region_id = d.region_id
WHERE o.status = 'COMPLETED'
  AND o.order_date >= DATE '2025-01-01' AND o.order_date < DATE '2026-01-01'
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3;
