SELECT product_code, product_name, category, unit_price
FROM products
WHERE segment = 'Farmasi' AND is_active
ORDER BY unit_price DESC, product_code;
