# Kasus 02: Pipeline gagal jam 2 pagi

**Tingkat:** sedang | **Waktu yang disarankan:** 20 menit | **Topik:** incident response, rerun aman, backfill, postmortem

## Konteks

Anda sedang on-call. Jam 02.10 Anda menerima alert dari Airflow:

```
DAG daily_sales_pipeline, run 2025-11-03, task load_fact_sales FAILED (attempt 3/3)
duckdb.ConstraintException / Snowflake: Duplicate key value violates unique constraint
"fact_sales_pk" on (order_item_id)
```

Informasi tambahan:

- Urutan task: `extract_branches >> stage_orders >> transform_orders >> load_fact_sales >> refresh_dashboard`.
- Task `extract_branches` dan `stage_orders` sukses. `transform_orders` sukses tetapi berjalan 3 kali lebih lama dari biasanya.
- Kemarin sore tim aplikasi cabang Surabaya melakukan migrasi dan "mengirim ulang" data 2 minggu terakhir.
- `load_fact_sales` memakai `INSERT INTO fact_sales SELECT ... FROM stg_orders_transformed`.
- Direksi membuka dashboard jam 07.30 untuk rapat mingguan.
- `retries=3` dengan `retry_delay=5 menit`; ketiga percobaan gagal dengan error yang sama.

## Pertanyaan

1. Apa langkah triase Anda dalam 15 menit pertama? Apa yang Anda cek, dan urutannya?
2. Apa kemungkinan akar masalahnya? Kenapa retry otomatis tidak membantu?
3. Apa perbaikan jangka pendek supaya dashboard siap jam 07.30, tanpa membuat data salah?
   Kapan Anda memilih menunda dashboard dan memberi pengumuman, alih-alih memaksa data masuk?
4. Bagaimana Anda mengubah task load supaya aman di-rerun (idempotent)?
5. Kalau ternyata data 2 minggu terakhir di fact_sales sudah terduplikasi oleh proses lain,
   bagaimana Anda memperbaikinya (backfill)? Apa risiko `catchup` di Airflow pada situasi ini?
6. Apa isi postmortem Anda dan tindakan pencegahan apa yang Anda usulkan?
7. Siapa yang Anda kabari, kapan, dan isi pesannya apa?

## Jawaban Saya

<!-- Tulis jawaban Anda di bawah ini. -->
