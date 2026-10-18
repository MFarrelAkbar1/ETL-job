-- Trik klasik: tanggal dikurangi nomor urut. Tanggal yang berurutan menghasilkan
-- nilai g yang sama, sehingga setiap pulau (island) bisa di-GROUP BY.
WITH days AS (
    SELECT DISTINCT o.distributor_id, o.order_date
    FROM orders_clean o
    JOIN distributors d ON d.distributor_id = o.distributor_id
    WHERE o.order_date >= DATE '2025-01-01' AND o.order_date < DATE '2026-01-01'
),
grp AS (
    SELECT *, order_date - CAST(ROW_NUMBER() OVER (PARTITION BY distributor_id ORDER BY order_date) AS INTEGER) AS g
    FROM days
),
islands AS (
    SELECT distributor_id, MIN(order_date) AS streak_start, MAX(order_date) AS streak_end, COUNT(*) AS len
    FROM grp
    GROUP BY distributor_id, g
)
SELECT distributor_id, len AS longest_streak_days, streak_start, streak_end
FROM islands
QUALIFY ROW_NUMBER() OVER (PARTITION BY distributor_id ORDER BY len DESC, streak_start) = 1
ORDER BY longest_streak_days DESC, distributor_id;
