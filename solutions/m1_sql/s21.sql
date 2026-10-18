-- Langkah 0: bandingkan snapshot dengan baris current. IS DISTINCT FROM menangani NULL.
CREATE TEMP TABLE scd_changes AS
SELECT s.*,
       c.distributor_id IS NULL AS is_new,
       c.distributor_id IS NOT NULL AND (
           s.region_id IS DISTINCT FROM c.region_id
        OR s.city      IS DISTINCT FROM c.city
        OR s.address   IS DISTINCT FROM c.address) AS type2_changed,
       c.distributor_id IS NOT NULL
        AND s.distributor_name IS DISTINCT FROM c.distributor_name AS name_changed
FROM distributor_snapshot s
LEFT JOIN dim_distributor_scd2 c
  ON c.distributor_id = s.distributor_id AND c.is_current;

-- Langkah 1: SCD Type 1 untuk nama, hanya kalau tidak ada perubahan Type 2.
UPDATE dim_distributor_scd2 AS t
SET distributor_name = ch.distributor_name
FROM scd_changes ch
WHERE t.distributor_id = ch.distributor_id AND t.is_current
  AND ch.name_changed AND NOT ch.type2_changed;

-- Langkah 2: tutup baris lama yang atribut Type 2-nya berubah.
UPDATE dim_distributor_scd2 AS t
SET valid_to = DATE '2025-07-01', is_current = FALSE
FROM scd_changes ch
WHERE t.distributor_id = ch.distributor_id AND t.is_current AND ch.type2_changed;

-- Langkah 3: insert versi baru + distributor baru.
INSERT INTO dim_distributor_scd2
SELECT (SELECT MAX(distributor_sk) FROM dim_distributor_scd2)
         + ROW_NUMBER() OVER (ORDER BY distributor_id) AS distributor_sk,
       distributor_id, distributor_name, region_id, city, address,
       DATE '2025-07-01' AS valid_from, DATE '9999-12-31' AS valid_to, TRUE AS is_current
FROM scd_changes
WHERE type2_changed OR is_new;

DROP TABLE scd_changes;
