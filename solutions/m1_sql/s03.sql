-- COUNT(kolom dari tabel kanan) bernilai 0 untuk region tanpa pasangan, COUNT(*) bernilai 1.
SELECT r.region_id, r.region_name,
       COUNT(d.distributor_id)                            AS n_distributors,
       COUNT(d.distributor_id) FILTER (WHERE d.is_active) AS n_active
FROM regions r
LEFT JOIN distributors d ON d.region_id = r.region_id
GROUP BY r.region_id, r.region_name
ORDER BY r.region_id;
