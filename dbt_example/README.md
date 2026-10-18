# Bonus Modul 4: dbt-duckdb

Contoh kecil proyek dbt yang membaca tabel mentah dari `data/warehouse.duckdb`
(di-attach read-only), membangun model staging, lalu menjalankan **data test**:
`unique`, `not_null`, `relationships`, `accepted_values`, dan satu singular test.

## Setup (sekali, butuh internet)

```bash
task dbt-setup      # membuat .venv-dbt terpisah dan menginstall dbt-duckdb
```

## Menjalankan

```bash
task dbt-build      # dbt build = run model + jalankan semua test
```

Hasilnya sengaja **tidak semuanya hijau**. Beberapa test berstatus `WARN` karena data mentah
memang kotor (distributor orphan, harga negatif). Itu disengaja: lihat bagaimana `severity`
menentukan apakah pipeline berhenti atau hanya memberi peringatan.

## Struktur

```
models/
  sources.yml              definisi source (tabel mentah di warehouse.duckdb)
  staging/
    stg_orders.sql         dedup order_id (versi terbaru) + parse 3 format tanggal
    stg_order_items.sql    normalisasi product_code
    schema.yml             test generic per kolom
  marts/
    fct_sales_daily.sql    revenue harian per distributor (bergantung pada kedua staging)
tests/
  assert_unit_price_positive.sql   singular test: query yang mengembalikan baris BERMASALAH
```

## Latihan (dinilai sendiri)

1. Jalankan `task dbt-build`. Catat test mana yang `PASS`, `WARN`, dan kenapa.
2. Ubah `severity` test `not_null` pada `stg_orders.order_date` menjadi `error`, jalankan
   `task dbt-build`. Apa yang terjadi pada `fct_sales_daily`? Kembalikan ke `warn`, lalu ulangi
   dengan test `relationships` distributor. Apakah `fct_sales_daily` diperlakukan sama? Kenapa?
   Kembalikan lagi ke `warn` setelahnya.
3. Tambahkan test `not_null` untuk `stg_order_items.unit_price`. Harus berstatus apa?
4. Tambahkan `accepted_values` untuk `stg_orders.channel` dengan nilai yang benar (lihat data).
5. Tulis singular test baru `tests/assert_no_future_orders.sql` yang gagal kalau ada
   `order_date` di masa depan.
6. Pertanyaan interview: kenapa `relationships` di sini dipasang di staging dan bukan di
   tabel mentah (source)? Kapan Anda memasang test di source?

Kunci jawaban latihan ini ada di `solutions/m4_quality/dbt_jawaban.md`.
