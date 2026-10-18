# Kasus 05: Stok near real-time dan data resep pasien

**Tingkat:** sulit | **Waktu yang disarankan:** 25 menit | **Topik:** batch vs streaming, CDC, lakehouse, governance, UU PDP

## Konteks

Tim supply chain ingin melihat stok setiap gudang **maksimal 5 menit terlambat** dari kondisi
sebenarnya, untuk mencegah kehabisan obat. Sumbernya database MySQL di sistem gudang (WMS),
tabel `stock_movement` (setiap barang masuk, keluar, dan penyesuaian), sekitar 2 juta baris
per hari dengan puncak saat tutup bulan.

Bersamaan dengan itu, tim apotek klinik mitra mulai mengirim data **resep**: nama pasien, NIK,
nomor telepon, diagnosis, dan obat yang diresepkan. Tim data science ingin memakai data resep
untuk forecasting permintaan obat per kota.

Platform yang tersedia: object storage, Kafka, Spark Structured Streaming, dan lakehouse
(Delta Lake atau Apache Iceberg) dengan catalog terpusat.

## Pertanyaan

1. Apakah kebutuhan stok ini benar-benar butuh streaming? Bandingkan dengan micro-batch
   setiap 5 menit. Apa pertanyaan yang Anda ajukan ke pengguna sebelum memutuskan?
2. Rancang alur CDC dari MySQL sampai tabel stok terkini di lakehouse. Bagaimana menangani
   event yang datang terlambat, duplikat, atau urutannya tertukar? Bagaimana menjamin hasil
   tetap benar kalau job restart?
3. Masalah apa yang muncul pada tabel lakehouse yang di-update tiap beberapa menit
   (small files, snapshot menumpuk), dan bagaimana mengatasinya?
4. Data resep berisi data pribadi dan **data pribadi yang bersifat spesifik** (data kesehatan)
   menurut UU PDP No. 27 Tahun 2022. Apa kewajiban perusahaan sebagai pengendali data?
5. Rancang kontrol akses: siapa boleh melihat apa? Jelaskan pemakaian RBAC, column masking,
   dan row-level security. Bagaimana tim data science tetap bisa forecasting tanpa melihat
   identitas pasien?
6. Apa yang Anda lakukan kalau terjadi kebocoran data resep?

## Jawaban Saya

<!-- Tulis jawaban Anda di bawah ini. -->
