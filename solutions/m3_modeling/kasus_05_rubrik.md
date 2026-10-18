# Rubrik Kasus 05: Stok near real-time dan data resep (UU PDP)

Skor 0/1/2 per kriteria, total maksimal 18. Target: **12 ke atas**.

| # | Kriteria | Skor 2 kalau jawaban memuat |
|---|---|---|
| 1 | Streaming vs micro-batch | Menanyakan keputusan apa yang diambil dari data, berapa latensi yang benar-benar dibutuhkan, biaya yang diterima. Latensi 5 menit bisa dipenuhi micro-batch (misalnya Spark Structured Streaming trigger 1 sampai 5 menit) dengan operasional lebih sederhana daripada streaming per event |
| 2 | Alur CDC | Debezium membaca binlog MySQL, menulis ke Kafka (topic per tabel, key = primary key), Spark membaca Kafka dan MERGE ke tabel bronze/silver di Delta/Iceberg, tabel stok terkini (gold) sebagai agregat per gudang x produk |
| 3 | Duplikat dan urutan | Dedup berdasarkan primary key + posisi log (LSN/binlog offset) atau `updated_at`, MERGE hanya kalau event lebih baru, partisi Kafka per key menjaga urutan per key. Watermark untuk event terlambat |
| 4 | Exactly-once / restart | Checkpoint Spark menyimpan offset, sink idempotent (MERGE), sehingga reprocess setelah restart tidak menggandakan data. Menyebut bahwa "exactly-once end-to-end" bergantung pada sink yang idempotent atau transaksional |
| 5 | Pemeliharaan tabel | Small files: compaction (`OPTIMIZE` di Delta, `rewrite_data_files` di Iceberg), expire snapshot/`VACUUM` untuk membuang file lama, partisi yang masuk akal, Z-order/sort untuk kolom filter |
| 6 | Kewajiban UU PDP | Data kesehatan termasuk data pribadi spesifik (Pasal 4). Dasar pemrosesan yang sah (persetujuan eksplisit atau dasar lain di Pasal 20), pembatasan tujuan, DPIA untuk pemrosesan berisiko tinggi, Pejabat Pelindungan Data Pribadi untuk pemrosesan data spesifik skala besar, retensi terbatas, hak subjek data (akses, koreksi, hapus, tarik persetujuan), aturan transfer ke luar negeri |
| 7 | RBAC, masking, RLS | Role per fungsi (supply_chain, data_science, apoteker, auditor), least privilege. Column masking untuk NIK/nama/telepon (misalnya hanya role tertentu melihat nilai asli). Row-level security agar apotek/region hanya melihat datanya sendiri. Ditegakkan di catalog/engine (Unity Catalog, Polaris/Ranger, Snowflake policy), bukan di aplikasi |
| 8 | Forecasting tanpa identitas | Data science cukup data agregat atau pseudonim: buang/hash NIK dengan salt yang disimpan terpisah (pseudonimisasi masih data pribadi), agregasi per kota x obat x minggu, minimum ukuran grup, diagnosis digeneralisasi |
| 9 | Respons kebocoran | Hentikan dan batasi akses, investigasi cakupan, notifikasi tertulis ke subjek data dan lembaga pelindungan data paling lambat 3 x 24 jam (Pasal 46) berisi data yang terungkap, kapan dan bagaimana, serta upaya penanganan. Dokumentasi dan perbaikan kontrol |

## Catatan fakta UU PDP (cek ulang ke teks resmi sebelum interview)

- UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi, diundangkan 17 Oktober 2022, masa
  penyesuaian 2 tahun (berlaku penuh Oktober 2024).
- Pasal 4: data pribadi spesifik meliputi antara lain data dan informasi kesehatan, biometrik,
  genetika, catatan kejahatan, data anak, dan data keuangan pribadi.
- Pasal 20: dasar pemrosesan, antara lain persetujuan yang sah secara eksplisit, kewajiban
  perjanjian, kewajiban hukum, kepentingan vital, tugas kepentingan umum, kepentingan yang sah.
- Pasal 46: notifikasi kegagalan pelindungan data pribadi paling lambat 3 x 24 jam.
- Sanksi administratif bisa berupa denda sampai 2% dari pendapatan tahunan, selain sanksi pidana
  untuk perbuatan tertentu.

## Red flag

- Memberi tim data science akses ke tabel resep mentah "karena internal".
- Menganggap hashing NIK membuat data tidak lagi data pribadi.
- Langsung memilih streaming per event tanpa bertanya kebutuhan latensi.
