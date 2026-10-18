# Rubrik Kasus 04: Star schema distribusi farmasi

Skor 0/1/2 per kriteria, total maksimal 18. Target: **12 ke atas**.

| # | Kriteria | Skor 2 kalau jawaban memuat |
|---|---|---|
| 1 | Fact penjualan | `fact_sales_line`, grain satu baris per item order (atau per item invoice), transaction fact, measure quantity, gross_amount, discount_amount, net_amount (additive) |
| 2 | Fact target | `fact_sales_target`, grain sales rep x kategori x bulan, measure target_amount. Sadar grain-nya berbeda dari fact penjualan |
| 3 | Fact stok | `fact_inventory_daily`, periodic snapshot per gudang x produk x batch x hari, measure qty_on_hand, nilai stok (semi-additive: boleh dijumlah antar gudang, tidak antar hari), days_to_expiry dihitung dari dim_batch |
| 4 | Fact fulfillment | `fact_order_fulfillment`, accumulating snapshot per order, beberapa role-playing date (order, approved, picked, shipped, received), measure lag hari per tahap. Baris di-update saat milestone tercapai |
| 5 | Factless promosi | `fact_promotion_coverage`, factless, grain promosi x distributor x hari (atau periode). Untuk menemukan promosi tanpa penjualan: coverage EXCEPT/anti join ke fact penjualan |
| 6 | Dimensi dan SCD | dim_date (role-playing), dim_product (Type 2 untuk category, Type 1 untuk koreksi nama), dim_distributor (Type 2 untuk region), dim_sales_rep, dim_warehouse, dim_promotion, dim_batch. Surrogate key, fact menyimpan surrogate key versi yang berlaku saat transaksi |
| 7 | Batch dan expiry | dim_batch (batch_no, product, tanggal produksi, expiry_date) karena atributnya melekat pada batch, bukan pada transaksi. Alternatif degenerate dimension di fact dibahas dengan trade-off |
| 8 | Target vs aktual | Agregasikan penjualan ke grain target dulu (rep x kategori x bulan) memakai dim_product.category dan dim_date.month, baru dibandingkan (drill-across). Tidak JOIN target ke baris penjualan langsung karena akan double counting |
| 9 | OBT / Data Vault | OBT: konsumsi BI sederhana, kolumnar murah, tetapi sulit dipelihara dan SCD jadi rumit. Data Vault: banyak sumber yang berubah, kebutuhan audit/historis penuh, sebagai lapisan integrasi di bawah star schema |

## Bus matrix model

| Fact \ Dimensi | date | product | batch | distributor | sales_rep | warehouse | promotion |
|---|---|---|---|---|---|---|---|
| fact_sales_line | X | X | X | X | X | X | X |
| fact_sales_target | X (bulan) | X (kategori) | | | X | | |
| fact_inventory_daily | X | X | X | | | X | |
| fact_order_fulfillment | X (banyak role) | | | X | X | X | |
| fact_promotion_coverage | X | X | | X | | | X |

## Red flag

- Satu fact table besar untuk semua kebutuhan dengan grain campur.
- Stok dijumlahkan antar hari ("total stok bulan Oktober").
- Region disimpan hanya sebagai atribut current tanpa SCD Type 2.
