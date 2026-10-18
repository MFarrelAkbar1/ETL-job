-- Satu kali scan, setiap metrik dipilah dengan FILTER (atau SUM(CASE WHEN ...)).
-- LEFT JOIN dari daftar segment menjaga segment tanpa transaksi tetap muncul, seperti query asli.
WITH agg AS (
    SELECT p.segment,
           SUM(oi.line_amount)         FILTER (WHERE o.order_date <  DATE '2025-01-01') AS rev_2024,
           SUM(oi.line_amount)         FILTER (WHERE o.order_date >= DATE '2025-01-01') AS rev_2025,
           COUNT(DISTINCT o.order_id)  FILTER (WHERE o.order_date >= DATE '2025-01-01') AS orders_2025,
           AVG(oi.quantity)            FILTER (WHERE o.order_date >= DATE '2025-01-01') AS avg_qty_2025
    FROM order_items_clean oi
    JOIN orders_clean o ON o.order_id = oi.order_id
    JOIN products p ON p.product_code = oi.product_code
    WHERE o.status = 'COMPLETED'
      AND o.order_date >= DATE '2024-01-01' AND o.order_date < DATE '2026-01-01'
    GROUP BY p.segment
)
SELECT s.segment, a.rev_2024, a.rev_2025, a.orders_2025, a.avg_qty_2025
FROM (SELECT DISTINCT segment FROM products) s
LEFT JOIN agg a USING (segment)
ORDER BY 1;
