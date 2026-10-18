# Kasus 01: Pipeline penjualan dari 12 database cabang ke warehouse

**Tingkat:** sedang | **Waktu yang disarankan:** 25 menit | **Topik:** ingestion, incremental load, medallion, idempotency

## Konteks

PT Sehat Sentosa (distributor farmasi dan consumer goods) punya 12 kantor cabang di Jawa,
Bali, Sulawesi, dan Papua. Setiap cabang menjalankan aplikasi penjualan sendiri:

- 9 cabang memakai PostgreSQL 12, 3 cabang (hasil akuisisi) memakai SQL Server 2016.
- Skema hampir sama, tetapi cabang hasil akuisisi memakai nama kolom berbeda
  (misalnya `kd_brg` alih-alih `product_code`) dan menyimpan harga dalam ribuan rupiah.
- Setiap cabang mencatat waktu dalam zona waktu lokal (WIB, WITA, WIT) tanpa informasi zona.
- Tabel `sales_order` punya kolom `last_modified`, tetapi beberapa aplikasi lupa memperbaruinya
  saat status order diubah lewat script admin.
- Order bisa dibatalkan sampai 14 hari setelah dibuat.
- Koneksi ke cabang Papua kadang putus beberapa jam.
- Volume total: sekitar 300 ribu baris order item per hari. Data historis 5 tahun.

Manajemen ingin dashboard penjualan nasional yang diperbarui **setiap pagi jam 06.00 WIB**,
di cloud data warehouse (anggap Snowflake atau Databricks).

## Pertanyaan

1. Gambarkan arsitektur end-to-end dari sumber sampai dashboard. Layer apa saja yang Anda buat
   dan apa isi masing-masing?
2. Strategi ekstraksi apa yang Anda pilih (full load, incremental berdasarkan timestamp, CDC)?
   Jelaskan trade-off-nya, dan bagaimana Anda menangani masalah `last_modified` yang tidak andal
   serta order yang bisa dibatalkan sampai 14 hari.
3. Bagaimana Anda menyeragamkan perbedaan skema, satuan harga, dan zona waktu antar cabang?
4. Bagaimana pipeline tetap benar kalau dijalankan ulang (rerun) atau kalau satu cabang
   terlambat datang? Jelaskan konsep idempotency di desain Anda.
5. Pengecekan data quality apa yang Anda pasang, dan di layer mana?
6. Bagaimana Anda memonitor dan memberi tahu pengguna kalau data satu cabang belum lengkap
   pada jam 06.00?

## Jawaban Saya

<!-- Tulis jawaban Anda di bawah ini. Boleh pakai poin-poin dan diagram ASCII. -->
