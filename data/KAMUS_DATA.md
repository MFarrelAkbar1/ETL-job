# Kamus Data

Perusahaan fiktif distributor **consumer goods** dan **farmasi** di Indonesia, periode
2024-01-01 sampai 2025-12-31. Semua tabel ada di `data/warehouse.duckdb`. Tabel mentah juga
tersedia sebagai CSV di `data/raw/` dan Parquet di `data/parquet/`.

Buka database secara interaktif:

```bash
.venv/Scripts/python.exe -c "import duckdb; duckdb.connect('data/warehouse.duckdb', read_only=True).sql('FROM orders LIMIT 5').show()"
```

## Definisi bisnis

| Istilah | Definisi |
|---|---|
| Revenue (standar) | `SUM(order_items_clean.line_amount)` untuk order di `orders_clean` dengan `status = 'COMPLETED'` |
| line_amount | `quantity * unit_price` (tanpa diskon) |
| Tahun / bulan order | Berdasarkan `order_date`, bukan `updated_at` |
| Orphan | `distributor_id` yang terisi tetapi tidak ada di `distributors` |

## Tabel mentah (KOTOR, sengaja)

| Tabel | Grain | Kolom penting | Kotoran yang disisipkan |
|---|---|---|---|
| `regions` | 1 baris per region | region_id, region_name, island_group | Region R10 tidak punya distributor |
| `distributors` | 1 baris per distributor | distributor_id, distributor_name, distributor_type, region_id, city, address, onboard_date, is_active | `city` NULL di beberapa baris |
| `products` | 1 baris per produk | product_id, product_code (format `PRD-0001`), product_name, segment (`Farmasi` / `Consumer Goods`), category, brand, unit_price, is_active, launch_date | Beberapa produk tidak pernah dipesan; banyak harga kembar |
| `orders` | 1 baris per **versi** order | order_id, order_date (VARCHAR), distributor_id, status, channel, updated_at | order_id duplikat (versi lama + kiriman ganda), format tanggal campur (`YYYY-MM-DD`, `DD/MM/YYYY`, `DD-Mon-YYYY`), tanggal NULL/rusak, distributor orphan dan NULL |
| `order_items` | 1 baris per item order | order_item_id, order_id, product_code, quantity, unit_price | product_code huruf kecil/spasi, unit_price negatif dan NULL, quantity NULL |
| `returns` | 1 baris per retur item | return_id, order_id, order_item_id, product_code, return_qty, return_date, reason, refund_amount | |

## Tabel bersih (ground truth)

| Tabel | Isi |
|---|---|
| `orders_clean` | 1 baris per order_id, order_date bertipe DATE. Orphan dan NULL distributor **tetap ada** (itu masalah referential integrity, bukan masalah format) |
| `order_items_clean` | product_code sudah seragam, harga dan quantity benar, sudah ada `line_amount` |

## Tabel bantu soal SQL

| Tabel | Dipakai di | Isi |
|---|---|---|
| `stg_sales`, `dwh_sales` | S19 | Penjualan Juni 2025 di staging vs warehouse, ada selisih yang disengaja |
| `dim_product`, `product_updates` | S20 | Dimensi produk dan batch perubahan (op: `I`, `U`, `D`) |
| `dim_distributor_scd2`, `distributor_snapshot` | S21 | Dimensi SCD2 awal dan snapshot per 2025-07-01 |
| `dim_distributor_hist` | S22 | Riwayat region distributor (SCD2, valid_to eksklusif) |
