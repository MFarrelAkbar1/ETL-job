MERGE INTO dim_product AS t
USING product_updates AS s
ON t.product_id = s.product_id
WHEN MATCHED AND s.op = 'D' THEN DELETE
WHEN MATCHED AND s.updated_at > t.updated_at THEN UPDATE SET
    product_code = s.product_code,
    product_name = s.product_name,
    category     = s.category,
    unit_price   = s.unit_price,
    is_active    = s.is_active,
    updated_at   = s.updated_at
WHEN NOT MATCHED AND s.op <> 'D' THEN INSERT
    (product_id, product_code, product_name, category, unit_price, is_active, updated_at)
    VALUES (s.product_id, s.product_code, s.product_name, s.category, s.unit_price, s.is_active, s.updated_at);

-- Alternatif tanpa MERGE (engine lama):
--   DELETE FROM dim_product WHERE product_id IN (SELECT product_id FROM product_updates WHERE op = 'D');
--   UPDATE dim_product t SET ... FROM product_updates s
--     WHERE t.product_id = s.product_id AND s.op <> 'D' AND s.updated_at > t.updated_at;
--   INSERT INTO dim_product SELECT ... FROM product_updates s
--     WHERE s.op <> 'D' AND NOT EXISTS (SELECT 1 FROM dim_product t WHERE t.product_id = s.product_id);
