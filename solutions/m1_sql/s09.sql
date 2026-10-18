-- Agregasi item dan returns DIPISAH dulu, baru digabung. Kalau keduanya di-JOIN langsung
-- ke orders, setiap item terduplikasi sebanyak jumlah return di order itu (fan-out).
WITH base_orders AS (
    SELECT o.order_id, d.region_id
    FROM orders_clean o
    JOIN distributors d ON d.distributor_id = o.distributor_id
    WHERE o.status = 'COMPLETED'
      AND o.order_date >= DATE '2025-01-01' AND o.order_date < DATE '2026-01-01'
),
gross AS (
    SELECT b.region_id, SUM(oi.line_amount) AS gross_revenue
    FROM base_orders b JOIN order_items_clean oi ON oi.order_id = b.order_id
    GROUP BY b.region_id
),
refund AS (
    SELECT b.region_id, SUM(r.refund_amount) AS refund_amount
    FROM base_orders b JOIN returns r ON r.order_id = b.order_id
    GROUP BY b.region_id
)
SELECT g.region_id, rg.region_name,
       ROUND(g.gross_revenue, 2)                                      AS gross_revenue,
       ROUND(COALESCE(f.refund_amount, 0), 2)                         AS refund_amount,
       ROUND(g.gross_revenue - COALESCE(f.refund_amount, 0), 2)       AS net_revenue,
       ROUND(COALESCE(f.refund_amount, 0) / g.gross_revenue * 100, 2) AS return_rate_pct
FROM gross g
LEFT JOIN refund f USING (region_id)
JOIN regions rg ON rg.region_id = g.region_id
ORDER BY net_revenue DESC;
