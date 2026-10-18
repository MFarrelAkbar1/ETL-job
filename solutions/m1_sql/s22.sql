SELECT h.region_id, r.region_name, CAST(year(o.order_date) AS INTEGER) AS year,
       ROUND(SUM(oi.line_amount), 2) AS revenue
FROM orders_clean o
JOIN order_items_clean oi ON oi.order_id = o.order_id
JOIN dim_distributor_hist h
  ON h.distributor_id = o.distributor_id
 AND o.order_date >= h.valid_from
 AND o.order_date <  h.valid_to
JOIN regions r ON r.region_id = h.region_id
WHERE o.status = 'COMPLETED'
GROUP BY ALL
ORDER BY year, h.region_id;
