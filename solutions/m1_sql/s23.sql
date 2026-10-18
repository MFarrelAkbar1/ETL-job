-- Hitung total per order sekali, lalu rata-rata per distributor dengan window function.
-- Perhatikan: correlated subquery "o2.distributor_id = o.distributor_id" tidak pernah cocok
-- untuk distributor_id NULL, sedangkan PARTITION BY mengelompokkan semua NULL bersama.
-- Jadi NULL harus dibuang eksplisit supaya hasilnya identik.
WITH order_totals AS (
    SELECT o.order_id, o.distributor_id, SUM(oi.line_amount) AS order_total
    FROM orders_clean o
    JOIN order_items_clean oi ON oi.order_id = o.order_id
    WHERE o.status = 'COMPLETED'
      AND o.distributor_id IS NOT NULL
      AND o.order_date BETWEEN DATE '2025-01-01' AND DATE '2025-12-31'
    GROUP BY o.order_id, o.distributor_id
)
SELECT order_id, distributor_id, order_total
FROM order_totals
QUALIFY order_total > 2 * AVG(order_total) OVER (PARTITION BY distributor_id)
ORDER BY distributor_id, order_id;
