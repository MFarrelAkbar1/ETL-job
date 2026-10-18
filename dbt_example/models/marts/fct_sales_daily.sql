-- Mart sederhana: revenue harian per distributor. Bergantung pada kedua model staging,
-- sehingga kalau test berseverity error di staging gagal, model ini di-SKIP oleh dbt build.
{{ config(materialized = 'table') }}

select
    o.order_date,
    o.distributor_id,
    count(distinct o.order_id) as n_orders,
    sum(i.line_amount)         as revenue
from {{ ref('stg_orders') }} o
join {{ ref('stg_order_items') }} i on i.order_id = o.order_id
where o.status = 'COMPLETED'
  and o.order_date is not null
  and i.unit_price > 0
group by 1, 2
