-- Cara 1: NOT EXISTS (aman terhadap NULL)
SELECT p.product_id, p.product_code, p.product_name, p.is_active
FROM products p
WHERE NOT EXISTS (SELECT 1 FROM order_items_clean oi WHERE oi.product_code = p.product_code)
ORDER BY p.product_id;

-- Cara 2: LEFT JOIN ... IS NULL
-- SELECT p.product_id, p.product_code, p.product_name, p.is_active
-- FROM products p LEFT JOIN order_items_clean oi ON oi.product_code = p.product_code
-- WHERE oi.order_item_id IS NULL ORDER BY p.product_id;
--
-- NOT IN berbahaya: kalau subquery mengandung satu saja NULL, "x NOT IN (...)" bernilai
-- NULL untuk semua baris, sehingga hasilnya kosong.
