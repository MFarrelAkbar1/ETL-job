# Rubrik Kasus 01: Pipeline 12 cabang ke warehouse

Skor tiap kriteria: **0** = tidak dibahas, **1** = dibahas tapi dangkal/ada kesalahan,
**2** = lengkap dengan trade-off. Total maksimal 20. Target siap interview: **14 ke atas**.

| # | Kriteria | Skor 2 kalau jawaban memuat |
|---|---|---|
| 1 | Arsitektur berlapis | Layer jelas: landing/raw (bronze) apa adanya + metadata ingest, staging/silver (dibersihkan, diseragamkan, dedup), mart/gold (star schema, metrik). Raw disimpan supaya bisa replay. Menyebut orkestrator (Airflow) dan tempat transformasi (dbt/SQL) |
| 2 | Strategi ekstraksi | Membandingkan full load, incremental timestamp, dan CDC (log-based, misalnya Debezium atau fitur CDC SQL Server). Memilih dengan alasan volume (300 ribu/hari kecil) dan keandalan |
| 3 | `last_modified` tidak andal | Salah satu: CDC berbasis log (tidak bergantung kolom), atau **sliding window**: tarik ulang 14 sampai 15 hari terakhir setiap hari lalu MERGE, atau full refresh berkala untuk koreksi. Menyebut lookback/overlap window |
| 4 | Pembatalan 14 hari | Data 14 hari terakhir dianggap "belum final", diproses ulang setiap hari. Fact di-upsert berdasarkan key, bukan append |
| 5 | Penyeragaman skema | Mapping kolom per sumber (config/YAML atau model staging per sistem), konversi satuan harga (ribuan ke rupiah) di staging, tipe data seragam, kolom `source_system`/`branch_id` |
| 6 | Zona waktu | Simpan waktu asli + zona waktu cabang dari master cabang, konversi ke UTC (atau WIB sebagai standar laporan) di staging. Sadar bahwa cut-off harian berubah (order 23.30 WIT = 21.30 WIB) |
| 7 | Idempotency | Rerun tanggal yang sama memberi hasil sama: partisi per tanggal di-overwrite, atau MERGE berdasarkan natural key (branch_id + order_id + line_no). Tidak ada INSERT buta. Batch id/load_date dicatat |
| 8 | Data terlambat (Papua) | Pipeline per cabang independen, cabang yang terlambat tidak memblokir yang lain, diproses saat datang (sensor/retry), dan window lookback menangkap data terlambat |
| 9 | Data quality | Contoh konkret per layer: jumlah baris sumber vs landing, not null & unique key, referential integrity produk/distributor, nilai harga > 0, freshness per cabang, rekonsiliasi total harian vs sumber. Aksi saat gagal (blokir vs warning) |
| 10 | Monitoring & komunikasi | Tabel status kelengkapan per cabang (last successful load, row count), alert ke on-call, banner/indikator di dashboard "data cabang X per tanggal Y", SLA jelas |

## Poin jawaban model (ringkas)

```
Cabang (PG/MSSQL) --CDC atau extract incremental dengan lookback 15 hari--> Object storage / landing (raw, per cabang per tanggal load)
  --> staging (mapping skema, satuan, UTC, dedup per natural key, DQ checks)
  --> core/silver (orders, order_items gabungan nasional, MERGE)
  --> mart/gold (fact_sales, dim_product, dim_distributor SCD2, dim_date) --> dashboard
Orkestrasi: Airflow, 1 task group per cabang, lalu task gabungan dengan trigger rule yang sengaja dipilih.
```

- Natural key gabungan wajib karena order_id antar cabang bisa bentrok.
- Lookback window 15 hari: biaya kecil (300 ribu x 15 = 4,5 juta baris), menghilangkan
  ketergantungan pada `last_modified` dan menangkap pembatalan.
- Batas mulai dashboard: kalau cabang belum lengkap jam 05.30, tetap publish dengan penanda
  per cabang daripada menahan seluruh dashboard. Ini keputusan bisnis, tanyakan ke pengguna.

## Red flag (kurangi skor kalau muncul)

- Hanya full load setiap hari tanpa mempertimbangkan volume 5 tahun.
- Incremental berdasarkan `last_modified` tanpa menyadari masalahnya.
- `INSERT INTO fact` tanpa dedup/upsert.
- Mengabaikan zona waktu atau satuan harga.
- Tidak ada cara mengetahui data cabang mana yang belum masuk.
