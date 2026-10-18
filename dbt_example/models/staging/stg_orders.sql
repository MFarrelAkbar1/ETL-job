-- Satu baris per order_id (versi updated_at terbaru), tanggal sudah bertipe DATE.
with ranked as (
    select
        *,
        row_number() over (partition by order_id order by updated_at desc) as rn
    from {{ source('raw', 'orders') }}
)

select
    order_id,
    coalesce(
        try_strptime(order_date, '%Y-%m-%d'),
        try_strptime(order_date, '%d/%m/%Y'),
        try_strptime(order_date, '%d-%b-%Y')
    )::date as order_date,
    distributor_id,
    status,
    channel,
    updated_at
from ranked
where rn = 1
