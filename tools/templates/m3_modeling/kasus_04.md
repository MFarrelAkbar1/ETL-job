# Kasus 04: Star schema untuk analitik distribusi farmasi

**Tingkat:** sulit | **Waktu yang disarankan:** 30 menit | **Topik:** dimensional modeling, grain, SCD, jenis fact table

## Konteks

Divisi farmasi ingin satu model data untuk menjawab pertanyaan berikut:

1. Berapa penjualan per produk, per distributor, per region, per bulan, dan bagaimana trennya?
2. Berapa pencapaian sales rep dibanding **target bulanan per kategori produk**?
3. Produk apa yang stoknya di gudang hampir habis atau mendekati **tanggal kedaluwarsa (expiry)**,
   per nomor batch?
4. Berapa lama rata-rata waktu dari order dibuat sampai barang diterima distributor, dan di
   tahap mana paling lama (approval, picking, pengiriman)?
5. Ketika distributor pindah region atau produk berganti kategori, laporan historis harus tetap
   memakai kondisi pada saat transaksi terjadi.
6. Promosi mana yang dijalankan di distributor mana, termasuk promosi yang **tidak menghasilkan
   penjualan** sama sekali.

## Pertanyaan

1. Tentukan fact table yang Anda buat. Untuk masing-masing: nama, grain (dalam satu kalimat),
   jenis fact (transaction, periodic snapshot, accumulating snapshot, factless), dan measure.
2. Tentukan dimension table beserta atribut penting. Mana yang SCD Type 1 dan mana Type 2?
3. Gambarkan bus matrix sederhana (fact vs dimension).
4. Bagaimana Anda memodelkan nomor batch dan tanggal expiry? Dimensi sendiri atau atribut di fact?
5. Target ada di level kategori per bulan, penjualan di level produk per hari. Bagaimana
   membandingkan keduanya tanpa double counting?
6. Kapan Anda akan memilih One Big Table (OBT) atau model Data Vault dibanding star schema?

## Jawaban Saya

<!-- Tulis jawaban Anda di bawah ini. Diagram ASCII sangat dianjurkan. -->
