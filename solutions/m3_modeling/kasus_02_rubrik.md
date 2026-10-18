# Rubrik Kasus 02: Pipeline gagal jam 2 pagi

Skor 0/1/2 per kriteria, total maksimal 16. Target: **11 ke atas**.

| # | Kriteria | Skor 2 kalau jawaban memuat |
|---|---|---|
| 1 | Triase terstruktur | Akui alert, baca log task yang gagal, cek apa yang berubah (migrasi Surabaya), cek volume staging vs hari biasa (transform 3x lebih lama = sinyal volume naik), cek apakah ada partial write di fact. Tidak langsung "clear and rerun" |
| 2 | Akar masalah | Data dikirim ulang menyebabkan duplikat order_item_id di staging (atau tumpang tindih dengan data yang sudah ada di fact). `INSERT` buta melanggar primary key. Error deterministik, jadi retry tidak membantu; retry hanya berguna untuk error transien |
| 3 | Perbaikan jangka pendek | Dedup staging (ambil versi terbaru per key), ubah load menjadi MERGE/upsert atau delete+insert per partisi tanggal, jalankan untuk run ini, validasi jumlah baris dan total vs hari sebelumnya, baru refresh dashboard |
| 4 | Keputusan tunda vs paksa | Kalau tidak yakin datanya benar sebelum 07.30, lebih baik dashboard memakai data kemarin dengan pengumuman jelas daripada menampilkan angka salah ke direksi. Menyebut prinsip "angka salah lebih berbahaya daripada angka terlambat" |
| 5 | Load idempotent | MERGE berdasarkan natural key, atau overwrite partisi `order_date`/`load_date` dalam transaksi. Dedup di staging sebelum load. Unique constraint/test sebagai pagar terakhir |
| 6 | Backfill dan catchup | Identifikasi rentang terdampak (2 minggu), jalankan ulang per tanggal dengan `airflow dags backfill -s ... -e ...` atau trigger per logical date, task harus idempotent. `catchup=True` pada DAG baru atau setelah DAG di-pause bisa memicu banyak run lama sekaligus dan membebani sumber; atur `max_active_runs` |
| 7 | Postmortem blameless | Timeline, dampak, akar masalah (5 whys), apa yang berjalan baik/buruk, action item dengan pemilik dan tenggat. Tidak menyalahkan individu |
| 8 | Pencegahan dan komunikasi | Data contract/notifikasi perubahan dari tim aplikasi, DQ check uniqueness di staging sebelum load (fail fast), alert volume anomali. Komunikasi: kabari atasan/stakeholder dashboard sebelum 07.00 dengan status, dampak, ETA; update lagi setelah selesai |

## Poin jawaban model

Contoh load idempotent:

```sql
MERGE INTO fact_sales t
USING (
  SELECT * FROM stg_orders_transformed
  QUALIFY ROW_NUMBER() OVER (PARTITION BY order_item_id ORDER BY updated_at DESC) = 1
) s
ON t.order_item_id = s.order_item_id
WHEN MATCHED AND s.updated_at > t.updated_at THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...;
```

Contoh pesan ke stakeholder (06.45):
> "Pipeline penjualan semalam gagal karena data duplikat dari migrasi cabang Surabaya.
> Dashboard saat ini menampilkan data sampai 2 November. Data 3 November sedang divalidasi,
> estimasi siap 08.30. Angka cabang lain tidak terdampak. Update berikutnya jam 08.00."

## Red flag

- Langsung menaikkan `retries` atau menghapus primary key supaya load lolos.
- Rerun tanpa memeriksa apakah ada data setengah termuat.
- Tidak mengabari siapa pun sampai direksi menemukan sendiri.
