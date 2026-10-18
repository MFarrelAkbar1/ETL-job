SELECT category, product_code, unit_price,
       ROW_NUMBER() OVER (PARTITION BY category ORDER BY unit_price DESC, product_code) AS rn,
       RANK()       OVER (PARTITION BY category ORDER BY unit_price DESC) AS rnk,
       DENSE_RANK() OVER (PARTITION BY category ORDER BY unit_price DESC) AS drnk
FROM products
QUALIFY drnk <= 5
ORDER BY category, rn;
-- Tanpa QUALIFY (engine lain): bungkus di subquery/CTE lalu WHERE drnk <= 5.
