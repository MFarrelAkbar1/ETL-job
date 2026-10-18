SELECT p.product_code, p.product_name,
       SUM(oi.quantity) AS total_qty,
       COUNT(*)         AS n_lines
FROM order_items oi
JOIN products p ON p.product_code = UPPER(TRIM(oi.product_code))
WHERE p.segment = 'Farmasi'
GROUP BY p.product_code, p.product_name
ORDER BY total_qty DESC, p.product_code;
