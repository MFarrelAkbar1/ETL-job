-- Agregasi per sisi DULU, baru FULL OUTER JOIN. Kalau di-JOIN di level baris, hasilnya meledak.
WITH s AS (SELECT order_date, COUNT(*) AS n, SUM(amount) AS amt FROM stg_sales GROUP BY 1),
     t AS (SELECT order_date, COUNT(*) AS n, SUM(amount) AS amt FROM dwh_sales GROUP BY 1),
     j AS (
        SELECT COALESCE(s.order_date, t.order_date) AS order_date,
               COALESCE(s.n, 0)   AS src_rows,   COALESCE(t.n, 0)   AS tgt_rows,
               COALESCE(s.amt, 0) AS src_amount, COALESCE(t.amt, 0) AS tgt_amount
        FROM s FULL OUTER JOIN t ON s.order_date = t.order_date
     )
SELECT order_date, src_rows, tgt_rows,
       ROUND(src_amount, 2) AS src_amount,
       ROUND(tgt_amount, 2) AS tgt_amount,
       tgt_rows - src_rows  AS row_diff,
       ROUND(tgt_amount - src_amount, 2) AS amount_diff,
       CASE WHEN tgt_rows = src_rows AND ROUND(tgt_amount - src_amount, 2) = 0
            THEN 'OK' ELSE 'MISMATCH' END AS status
FROM j
ORDER BY order_date;
