# Kasus 03: Angka dashboard beda dengan finance

**Tingkat:** sedang | **Waktu yang disarankan:** 20 menit | **Topik:** rekonsiliasi, definisi metrik, semantic layer

## Konteks

CFO mengirim pesan: "Revenue Oktober 2025 di dashboard Anda Rp 48,7 miliar, tetapi laporan
finance (dari ERP) Rp 47,1 miliar. Selisih 3,4%. Mana yang benar? Saya presentasi ke board
hari Jumat."

Yang Anda ketahui:

- Dashboard dihitung dari `fact_sales` di warehouse, sumbernya aplikasi penjualan cabang.
- Finance menghitung dari modul invoicing di ERP. Invoice dibuat saat barang **dikirim**, bukan
  saat order dibuat.
- Ada retur, diskon akhir bulan (credit note), dan order yang dibatalkan.
- Beberapa cabang di Indonesia Timur mencatat waktu dalam WITA/WIT.
- Dashboard memakai filter `status IN ('COMPLETED', 'SHIPPED')`.
- Tidak ada dokumen resmi definisi "revenue".

## Pertanyaan

1. Sebutkan minimal 6 kemungkinan penyebab selisih. Kelompokkan menjadi: perbedaan definisi,
   perbedaan waktu, dan masalah kualitas data.
2. Bagaimana metodologi rekonsiliasi Anda, langkah demi langkah? Data apa yang Anda minta dari
   finance? Pada level apa Anda membandingkan (total, per hari, per cabang, per invoice)?
3. Tulis sketsa query SQL rekonsiliasi yang akan Anda pakai (boleh pseudo-SQL).
4. Apa yang Anda sampaikan ke CFO hari ini, sebelum analisis selesai?
5. Apa solusi jangka panjang supaya angka tidak beda lagi?

## Jawaban Saya

<!-- Tulis jawaban Anda di bawah ini. -->
