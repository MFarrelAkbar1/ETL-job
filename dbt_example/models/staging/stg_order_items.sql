-- Kode produk diseragamkan supaya bisa di-join ke master products.
select
    order_item_id,
    order_id,
    upper(trim(product_code)) as product_code,
    quantity,
    unit_price,
    quantity * unit_price as line_amount
from {{ source('raw', 'order_items') }}
