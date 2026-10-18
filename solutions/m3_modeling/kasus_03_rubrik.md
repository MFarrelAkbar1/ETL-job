# Rubrik Kasus 03: Dashboard beda dengan finance

Skor 0/1/2 per kriteria, total maksimal 14. Target: **10 ke atas**.

| # | Kriteria | Skor 2 kalau jawaban memuat |
|---|---|---|
| 1 | Penyebab: definisi | Order (booking) vs invoice (billing), gross vs net (retur, credit note, diskon akhir bulan), status SHIPPED mungkin belum diinvoice, PPN termasuk atau tidak, pengakuan revenue finance mengikuti standar akuntansi |
| 2 | Penyebab: waktu | Order dibuat Oktober tetapi dikirim/diinvoice November (dan sebaliknya), cut-off zona waktu WITA/WIT, data terlambat masuk, laporan finance ditutup (closing) pada tanggal tertentu |
| 3 | Penyebab: kualitas data | Duplikat order di warehouse, order batal yang belum ter-update, mapping cabang/produk yang hilang, pembulatan, satuan harga |
| 4 | Metodologi rekonsiliasi | Mulai dari total, lalu pecah per hari, per cabang, sampai per dokumen (order_id/invoice_id). Minta data invoice level baris dari finance. Kategorikan setiap selisih (hanya di dashboard, hanya di ERP, ada di keduanya dengan nilai beda) dan kuantifikasi kontribusi tiap penyebab sampai selisih terjelaskan |
| 5 | Query rekonsiliasi | FULL OUTER JOIN di level dokumen setelah agregasi per sisi, kolom status (MATCH, ONLY_DWH, ONLY_ERP, AMOUNT_DIFF), ringkasan per kategori |
| 6 | Komunikasi ke CFO | Jawab cepat dan jujur: kedua angka bisa benar untuk definisi berbeda, untuk board pakai angka finance (revenue yang diakui) kecuali disepakati lain, berikan tenggat analisis. Jangan membela angka sendiri tanpa bukti |
| 7 | Solusi jangka panjang | Definisi metrik tertulis dan disepakati (metric dictionary/semantic layer), dashboard memberi label jelas ("Gross booking" vs "Net revenue"), sumber invoice ikut masuk warehouse, rekonsiliasi otomatis harian dengan threshold dan alert, data owner |

## Sketsa query model

```sql
WITH dwh AS (
  SELECT order_id, SUM(line_amount) AS amt FROM fact_sales
  WHERE order_date BETWEEN '2025-10-01' AND '2025-10-31' GROUP BY 1),
erp AS (
  SELECT order_id, SUM(net_amount) AS amt FROM erp_invoice_lines
  WHERE invoice_date BETWEEN '2025-10-01' AND '2025-10-31' GROUP BY 1)
SELECT CASE WHEN e.order_id IS NULL THEN 'ONLY_DWH'
            WHEN d.order_id IS NULL THEN 'ONLY_ERP'
            WHEN ABS(d.amt - e.amt) > 1 THEN 'AMOUNT_DIFF'
            ELSE 'MATCH' END AS category,
       COUNT(*) AS n_docs, SUM(COALESCE(d.amt, 0)) AS dwh_amt, SUM(COALESCE(e.amt, 0)) AS erp_amt
FROM dwh d FULL OUTER JOIN erp e USING (order_id)
GROUP BY 1;
```

Lanjutkan dengan drill-down kategori `ONLY_DWH` (biasanya order yang belum diinvoice atau
dibatalkan) dan `AMOUNT_DIFF` (biasanya retur/credit note).

## Red flag

- Langsung menyimpulkan salah satu sistem "salah".
- Mencoba "mengoreksi" angka dashboard dengan faktor pengali.
- Tidak menanyakan definisi revenue yang dipakai board.
