# Struktur metadata Apache Iceberg (ringkas)

```
catalog (di sini: SQLite)                 "sales.orders -> metadata/00003-....metadata.json"
   |
   v
metadata.json  (satu file per versi tabel, tidak pernah ditimpa)
   |  schema (semua versi, dengan field id), partition spec, properties,
   |  daftar snapshot, current-snapshot-id, metadata-log (versi metadata sebelumnya)
   v
snapshot  ->  manifest list  (snap-<id>-....avro, satu per snapshot)
                 |  daftar manifest + ringkasan partisi tiap manifest
                 v
              manifest file  (....-m0.avro)
                 |  daftar data file + statistik per kolom (min, max, null count)
                 |  + nilai partisi setiap file
                 v
              data file  (Parquet, di data/order_day=2025-01-02/...)
```

## Hal yang sering ditanyakan di interview

1. **Commit itu atomik karena apa?** Penulis membuat file data, manifest, manifest list, dan
   metadata.json BARU, lalu meminta catalog menukar pointer dari metadata lama ke yang baru
   (compare-and-swap). Kalau dua penulis bentrok, salah satu gagal dan harus retry. File lama
   tidak pernah diubah, sehingga pembaca selalu melihat versi yang konsisten.
2. **Snapshot** adalah keadaan lengkap tabel pada satu commit. Time travel = membaca snapshot
   lama. Snapshot lama baru benar-benar hilang setelah `expire_snapshots` (lalu file yatim
   dibersihkan dengan `remove_orphan_files`).
3. **Schema evolution aman** karena kolom diidentifikasi dengan **field id**, bukan nama atau
   posisi. Tambah, hapus, rename, dan reorder kolom hanya mengubah metadata. Data lama tidak
   ditulis ulang; kolom baru dibaca sebagai NULL dari file lama.
4. **Hidden partitioning**: spec `day(order_ts)` disimpan di metadata. User memfilter
   `order_ts`, Iceberg menerjemahkannya ke filter partisi. Statistik di manifest membuat
   file yang tidak relevan dilewati (pruning) tanpa listing folder.
5. **Partition evolution**: spec bisa diganti (misalnya bulan ke hari). File lama tetap memakai
   spec lama, file baru memakai spec baru.
6. **Kenapa tidak perlu `LIST` folder?** Daftar file ada di manifest. Di object storage, listing
   jutaan file itu lambat dan mahal; Iceberg menghindarinya.
7. **Delete di format v2**: copy-on-write (tulis ulang file) atau merge-on-read (position
   delete / equality delete file yang digabung saat baca). Compaction merapikannya.
8. **Bandingkan dengan Delta Lake**: Delta menyimpan log transaksi berurutan di `_delta_log/`
   (JSON per commit + checkpoint Parquet). Iceberg menyimpan pohon metadata
   (metadata.json, manifest list, manifest) dan mengandalkan catalog untuk pointer terkini.

## Cara melihat sendiri

Setelah `task iceberg-demo`, buka folder:

```
exercises/m6_iceberg/playground/warehouse/sales/orders/
  data/order_day=2025-01-01/...parquet
  metadata/00000-....metadata.json    <- versi 0 (tabel kosong)
  metadata/00001-....metadata.json    <- setelah append pertama
  metadata/snap-<id>-....avro         <- manifest list
  metadata/....-m0.avro               <- manifest
```

Buka file `.metadata.json` terbaru dengan editor teks dan cari `snapshots`, `schemas`,
`partition-specs`, dan `metadata-log`.
