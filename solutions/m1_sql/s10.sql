WITH parsed AS (
    SELECT order_id,
           COALESCE(
               TRY_STRPTIME(order_date, '%Y-%m-%d'),
               TRY_STRPTIME(order_date, '%d/%m/%Y'),
               TRY_STRPTIME(order_date, '%d-%b-%Y')
           )::DATE AS order_dt
    FROM orders
)
SELECT DATE_TRUNC('month', order_dt)::DATE AS order_month,
       COUNT(DISTINCT order_id)            AS n_orders
FROM parsed
GROUP BY 1
ORDER BY order_month NULLS LAST;
