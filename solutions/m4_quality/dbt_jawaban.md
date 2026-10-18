# Kunci jawaban latihan dbt (Modul 4 bonus)

1. **Hasil `dbt build` awal** (angka dari dataset seed tetap, `PASS=14 WARN=3`):
   - `PASS`: unique/not_null `stg_orders.order_id`, accepted_values `status`, unique/not_null
     `stg_order_items.order_item_id`, relationships `product_code` (lolos karena sudah
     dinormalisasi; di tabel mentah akan gagal), relationships `order_id`, test di source.
   - `WARN`: not_null `order_date` (250 tanggal rusak), relationships `distributor_id`
     (300 order orphan D901 sampai D905), `assert_unit_price_positive` (634 harga negatif).
   - Catatan: relationships tidak menghitung NULL sebagai gagal; distributor_id NULL lolos.

2. **Severity error** (diverifikasi dengan dbt Core 1.12.6):
   - `not_null` pada `order_date` = error: test `FAIL 250`, lalu `fct_sales_daily` di-**SKIP**
     (`ERROR=1 SKIP=1`) dan `dbt build` keluar dengan status gagal. Data buruk tidak mengalir
     ke mart.
   - `relationships` distributor = error: test `FAIL 300`, `dbt build` tetap keluar dengan
     status gagal, TETAPI `fct_sales_daily` tetap dibangun (`SKIP=0`). Test relationships punya
     dua parent (`stg_orders` dan source `distributors`), sehingga tidak dianggap "melekat" ke
     satu model, dan dbt tidak memakainya untuk memblokir model hilir.
   - Pelajaran: kalau sebuah pengecekan integritas harus benar-benar memblokir mart, jangan
     mengandalkan skip otomatis. Hentikan orkestrasi (Airflow) saat `dbt build` gagal, atau
     ubah pengecekannya menjadi test yang hanya punya satu parent.

3. **not_null unit_price**:
   ```yaml
   - name: unit_price
     data_tests:
       - not_null:
           config:
             severity: warn
   ```
   Hasilnya `WARN 457` (harga NULL yang sengaja disisipkan). Catatan: singular test
   `unit_price <= 0` tidak menangkap NULL, karena perbandingan dengan NULL bernilai NULL.

4. **accepted_values channel**: nilainya `Sales Rep`, `E-Order`, `Telesales`.
   ```yaml
   - name: channel
     data_tests:
       - accepted_values:
           arguments:
             values: ["Sales Rep", "E-Order", "Telesales"]
   ```

5. **Singular test**:
   ```sql
   select order_id, order_date
   from {{ ref('stg_orders') }}
   where order_date > current_date
   ```

6. **Di mana memasang test**: test di source mendeteksi masalah sedini mungkin dan cocok
   untuk asumsi yang HARUS benar dari sistem sumber (primary key master unik, kolom wajib
   terisi). Tetapi data mentah memang kotor (kode produk huruf kecil, duplikat versi order),
   sehingga test integritas yang bergantung pada pembersihan (relationships setelah
   normalisasi kode, unique setelah dedup) dipasang di staging. Prinsipnya: test sumber
   untuk kontrak dengan produsen data, test staging/mart untuk menjamin hasil transformasi.
