-- Singular test: dbt menganggap test GAGAL kalau query ini mengembalikan baris.
{{ config(severity = 'warn') }}

select order_item_id, unit_price
from {{ ref('stg_order_items') }}
where unit_price <= 0
