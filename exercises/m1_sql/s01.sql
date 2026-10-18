-- ==========================================================================
-- S01 | Filter dan sorting dasar
-- Tingkat: MUDAH | Prioritas: -
-- ==========================================================================
-- SOAL
--   Tampilkan semua produk dengan segment 'Farmasi' yang masih aktif (is_active = TRUE).
--
-- Tabel        : products
-- Kolom output : product_code, product_name, category, unit_price
-- Urutan baris : unit_price DESC, lalu product_code ASC
--
-- Definisi revenue standar: SUM(order_items_clean.line_amount) untuk order
-- di orders_clean dengan status = 'COMPLETED'.
--
-- Uji jawaban  : task test-sql -- -k s01
-- Petunjuk     : task hint -- s01   (3 level, dibuka bertahap)
-- ==========================================================================

-- Tulis jawaban Anda DI BAWAH baris ini

