"""Bank soal Modul 1 (SQL). Hanya berisi SOAL, tidak berisi jawaban.

File exercises/m1_sql/sXX.sql dibangkitkan dari sini oleh tools/render_exercises.py.
"""

REVENUE_RULE = (
    "Definisi revenue standar: SUM(order_items_clean.line_amount) untuk order di "
    "orders_clean dengan status = 'COMPLETED'."
)

QUESTIONS = [
    dict(
        id="s01", title="Filter dan sorting dasar", level="mudah", priority=False,
        tables="products",
        question="""Tampilkan semua produk dengan segment 'Farmasi' yang masih aktif (is_active = TRUE).""",
        columns="product_code, product_name, category, unit_price",
        order="unit_price DESC, lalu product_code ASC",
    ),
    dict(
        id="s02", title="INNER JOIN dan agregasi", level="mudah", priority=False,
        tables="orders_clean, order_items_clean, distributors",
        question="""Untuk setiap distributor yang ADA di master distributors, hitung jumlah order dan
revenue selama tahun 2025 (berdasarkan order_date). Gunakan definisi revenue standar.
Distributor tanpa order 2025 tidak perlu ditampilkan.""",
        columns="distributor_id, distributor_name, n_orders, revenue (dibulatkan 2 desimal)",
        order="revenue DESC",
    ),
    dict(
        id="s03", title="LEFT JOIN dan COUNT yang benar", level="mudah", priority=False,
        tables="regions, distributors",
        question="""Tampilkan SEMUA region (termasuk yang belum punya distributor) beserta jumlah
distributornya dan jumlah distributor yang aktif. Region tanpa distributor harus bernilai 0,
bukan 1 dan bukan NULL.""",
        columns="region_id, region_name, n_distributors, n_active",
        order="region_id ASC",
    ),
    dict(
        id="s04", title="GROUP BY dan HAVING", level="mudah", priority=True,
        tables="orders_clean, order_items_clean",
        question="""Cari distributor (distributor_id tidak NULL) yang pada tahun 2025 memenuhi DUA syarat
sekaligus: revenue minimal 1.500.000.000 DAN minimal 300 order. Gunakan definisi revenue
standar; order yang dihitung juga hanya yang COMPLETED.""",
        columns="distributor_id, n_orders, revenue (dibulatkan 2 desimal)",
        order="revenue DESC",
    ),
    dict(
        id="s05", title="Anti join: produk yang tidak pernah dipesan", level="mudah", priority=True,
        tables="products, order_items_clean",
        question="""Tampilkan produk di master products yang tidak pernah muncul sama sekali di
order_items_clean (status order apa pun). Coba tulis dengan 2 cara (NOT EXISTS dan
LEFT JOIN ... IS NULL), lalu pikirkan kenapa NOT IN berbahaya kalau kolomnya bisa NULL.""",
        columns="product_id, product_code, product_name, is_active",
        order="product_id ASC",
    ),
    dict(
        id="s06", title="Anti join pada data kotor: distributor yatim", level="mudah", priority=False,
        tables="orders_clean, order_items_clean, distributors",
        question="""Sebagian order punya distributor_id yang TIDAK ADA di master distributors (orphan).
Untuk setiap distributor_id orphan (abaikan yang NULL), hitung jumlah order (semua status)
dan revenue (hanya order COMPLETED). Ini adalah pengecekan referential integrity.""",
        columns="distributor_id, n_orders, revenue (dibulatkan 2 desimal)",
        order="distributor_id ASC",
    ),
    dict(
        id="s07", title="Normalisasi key sebelum JOIN", level="sedang", priority=False,
        tables="order_items (MENTAH), products",
        question="""Gunakan tabel MENTAH order_items. Kolom product_code di sana kotor: ada huruf kecil
dan spasi di depan atau belakang. Untuk setiap produk segment 'Farmasi', hitung total
quantity dan jumlah baris item (semua status order, quantity NULL diabaikan saat SUM tetapi
barisnya tetap dihitung di n_lines). Jangan sampai ada baris yang hilang karena beda format kode.""",
        columns="product_code (format master), product_name, total_qty, n_lines",
        order="total_qty DESC, lalu product_code ASC",
    ),
    dict(
        id="s08", title="Agregasi kondisional (pivot)", level="sedang", priority=False,
        tables="orders_clean, order_items_clean, products",
        question="""Buat tabel pivot revenue tahun 2025 per category (dari products) per kuartal.
Gunakan definisi revenue standar. Kuartal tanpa penjualan bernilai 0.""",
        columns="category, q1, q2, q3, q4, total (semua dibulatkan 2 desimal)",
        order="total DESC",
    ),
    dict(
        id="s09", title="CTE bertingkat: revenue bersih", level="sedang", priority=False,
        tables="orders_clean, order_items_clean, returns, distributors, regions",
        question="""Hitung revenue bersih per region untuk order tahun 2025 (berdasarkan order_date order
aslinya, bukan return_date). gross_revenue memakai definisi standar. refund_amount = total
returns.refund_amount untuk order COMPLETED tahun 2025 tersebut. net_revenue = gross - refund.
return_rate_pct = refund / gross * 100. Region diambil dari distributors (order orphan
dan NULL diabaikan). Hati-hati dengan fan-out saat JOIN dua tabel detail sekaligus.""",
        columns="region_id, region_name, gross_revenue, refund_amount, net_revenue, return_rate_pct (semua angka dibulatkan 2 desimal)",
        order="net_revenue DESC",
    ),
    dict(
        id="s10", title="Parsing tanggal dengan format campur", level="sedang", priority=False,
        tables="orders (MENTAH)",
        question="""Kolom orders.order_date bertipe VARCHAR dengan tiga format: 'YYYY-MM-DD', 'DD/MM/YYYY',
dan 'DD-Mon-YYYY' (contoh '14-Mar-2025'). Ada juga nilai NULL dan nilai rusak.
Hitung jumlah order UNIK (order_id) per bulan. Order yang tanggalnya tidak bisa di-parse
dikumpulkan dalam satu baris dengan order_month = NULL.""",
        columns="order_month (DATE, tanggal 1 di bulan tsb), n_orders",
        order="order_month ASC, baris NULL paling akhir",
    ),
    dict(
        id="s11", title="ROW_NUMBER vs RANK vs DENSE_RANK", level="sedang", priority=True,
        tables="products",
        question="""Di setiap category, ranking produk berdasarkan unit_price dari yang termahal.
Tampilkan ketiga jenis ranking: rn (ROW_NUMBER, kalau seri pakai product_code ASC),
rnk (RANK), dan drnk (DENSE_RANK). Hanya tampilkan baris dengan drnk <= 5.
Perhatikan perbedaan ketiganya pada produk dengan harga sama.""",
        columns="category, product_code, unit_price, rn, rnk, drnk",
        order="category ASC, rn ASC",
    ),
    dict(
        id="s12", title="Top N per grup", level="sedang", priority=True,
        tables="orders_clean, order_items_clean, products",
        question="""Cari 3 produk dengan revenue tertinggi di setiap category untuk tahun 2025.
Gunakan definisi revenue standar.""",
        columns="category, rank_in_category (1 sampai 3), product_code, product_name, revenue (2 desimal)",
        order="category ASC, rank_in_category ASC",
    ),
    dict(
        id="s13", title="Deduplikasi: ambil baris terbaru", level="sedang", priority=True,
        tables="orders (MENTAH)",
        question="""Tabel MENTAH orders punya order_id duplikat: sistem sumber mengirim beberapa versi
dari order yang sama, dan ada juga baris yang terkirim dua kali persis sama. Ambil SATU baris
per order_id, yaitu versi dengan updated_at paling baru. Hasil harus tepat satu baris per order_id.""",
        columns="order_id, order_date, distributor_id, status, channel, updated_at",
        order="order_id ASC",
    ),
    dict(
        id="s14", title="LAG: pertumbuhan bulan ke bulan", level="sedang", priority=True,
        tables="orders_clean, order_items_clean, products",
        question="""Hitung revenue bulanan per segment (dari products) untuk 2024 dan 2025, lalu bandingkan
dengan bulan sebelumnya di segment yang sama. Bulan pertama tiap segment punya prev_revenue
dan mom_pct NULL. mom_pct = (revenue - prev_revenue) / prev_revenue * 100.""",
        columns="segment, month (DATE tanggal 1), revenue, prev_revenue, mom_pct (angka dibulatkan 2 desimal)",
        order="segment ASC, month ASC",
    ),
    dict(
        id="s15", title="LEAD: jarak ke order berikutnya", level="sedang", priority=False,
        tables="orders_clean, distributors",
        question="""Untuk setiap distributor yang ada di master, ambil daftar TANGGAL UNIK ia melakukan
order (semua status) di tahun 2025. Untuk setiap tanggal, cari tanggal order berikutnya
(masih di 2025) dan selisih harinya. Tampilkan hanya jeda (gap) minimal 21 hari, yaitu
distributor yang lama tidak order. Kalau satu hari ada beberapa order, hitung sebagai satu tanggal.""",
        columns="distributor_id, order_date, next_order_date, gap_days (INTEGER)",
        order="distributor_id ASC, order_date ASC",
    ),
    dict(
        id="s16", title="Running total", level="sedang", priority=True,
        tables="orders_clean, order_items_clean, distributors",
        question="""Hitung revenue harian per region (region dari distributors, order orphan dan NULL
diabaikan) untuk 2024 dan 2025, lalu running total (kumulatif) per region yang
RESET setiap awal tahun. Hanya tanggal yang punya penjualan yang ditampilkan.""",
        columns="region_id, order_date, daily_revenue, running_revenue (2 desimal)",
        order="region_id ASC, order_date ASC",
    ),
    dict(
        id="s17", title="Moving average 7 hari dengan date spine", level="sulit", priority=True,
        tables="orders_clean, order_items_clean",
        question="""Untuk distributor 'D007', tampilkan revenue harian dan moving average 7 hari
(hari ini dan 6 hari sebelumnya) untuk SETIAP tanggal 2025-01-01 sampai 2025-03-31.
Hari tanpa penjualan tetap tampil dengan daily_revenue = 0 dan ikut dihitung dalam rata-rata.
Untuk 6 hari pertama, rata-rata dihitung dari hari yang tersedia mulai 1 Januari saja.
Petunjuk umum: distributor ini tidak order setiap hari.""",
        columns="order_date, daily_revenue, ma_7d (2 desimal)",
        order="order_date ASC (harus tepat 90 baris)",
    ),
    dict(
        id="s18", title="Gaps and islands: streak terpanjang", level="sulit", priority=False,
        tables="orders_clean, distributors",
        question="""Untuk setiap distributor di master, cari streak terpanjang hari BERTURUT-TURUT dengan
minimal 1 order (semua status) di tahun 2025. Kalau ada beberapa streak dengan panjang sama,
ambil yang paling awal. Distributor tanpa order 2025 tidak ditampilkan.""",
        columns="distributor_id, longest_streak_days, streak_start, streak_end",
        order="longest_streak_days DESC, distributor_id ASC",
    ),
    dict(
        id="s19", title="Rekonsiliasi jumlah baris dan total", level="sulit", priority=False,
        tables="stg_sales (sumber), dwh_sales (target)",
        question="""Tim finance curiga data warehouse tidak sama dengan staging. Bandingkan stg_sales dan
dwh_sales per order_date. Tanggal yang hanya ada di salah satu sisi tetap harus tampil,
dengan jumlah baris dan amount sisi yang kosong = 0.
row_diff = tgt_rows - src_rows, amount_diff = tgt_amount - src_amount.
status = 'OK' kalau row_diff = 0 dan amount_diff = 0, selain itu 'MISMATCH'.""",
        columns="order_date, src_rows, tgt_rows, src_amount, tgt_amount, row_diff, amount_diff, status (amount 2 desimal)",
        order="order_date ASC",
    ),
    dict(
        id="s20", title="MERGE / upsert ke dimensi", level="sulit", priority=True,
        tables="dim_product (target), product_updates (batch)", kind="dml",
        question="""Tulis statement (boleh MERGE INTO, atau kombinasi UPDATE/INSERT/DELETE) yang menerapkan
batch product_updates ke dim_product dengan aturan:
  1. op = 'D' dan product_id ada di target: hapus baris tersebut.
  2. op = 'D' tapi product_id tidak ada di target: abaikan.
  3. product_id sudah ada dan op <> 'D': update product_code, product_name, category,
     unit_price, is_active, updated_at, TETAPI hanya kalau updated_at di batch lebih baru dari
     updated_at di target (lindungi dari data basi).
  4. product_id belum ada dan op <> 'D': insert baris baru.
Statement Anda harus idempotent: dijalankan dua kali hasilnya sama.
Yang dinilai adalah isi akhir tabel dim_product.""",
        columns="(tidak ada SELECT, yang dicek isi dim_product)",
        order="-",
    ),
    dict(
        id="s21", title="SCD Type 2", level="sulit", priority=True,
        tables="dim_distributor_scd2 (target), distributor_snapshot (snapshot per 2025-07-01)", kind="dml",
        question="""Terapkan distributor_snapshot (kondisi per 2025-07-01) ke dim_distributor_scd2.
Konvensi: valid_to EKSKLUSIF, baris aktif punya valid_to = DATE '9999-12-31' dan is_current = TRUE.
Aturan:
  1. Atribut SCD Type 2: region_id, city, address. Kalau salah satu berubah (termasuk dari
     NULL ke ada isi), tutup baris lama (valid_to = DATE '2025-07-01', is_current = FALSE) dan
     buat baris baru (valid_from = DATE '2025-07-01').
  2. distributor_name adalah SCD Type 1: kalau HANYA nama yang berubah, timpa nama di baris
     current saja, tanpa versi baru. Kalau nama dan atribut Type 2 berubah bersamaan, baris
     lama tetap memakai nama lama dan baris baru memakai nama baru.
  3. Distributor baru (belum ada di dimensi): insert dengan valid_from = DATE '2025-07-01'.
  4. Distributor yang tidak muncul di snapshot: JANGAN diubah.
  5. distributor_sk baru = MAX(distributor_sk) yang ada + ROW_NUMBER() urut distributor_id.
     (Nilai sk tidak dibandingkan persis, tetapi harus unik dan tidak NULL.)
Statement Anda harus idempotent: dijalankan dua kali dengan snapshot yang sama, hasilnya sama.
Yang dinilai adalah isi akhir tabel dim_distributor_scd2.""",
        columns="(tidak ada SELECT, yang dicek isi dim_distributor_scd2)",
        order="-",
    ),
    dict(
        id="s22", title="Point-in-time join ke dimensi SCD2", level="sulit", priority=False,
        tables="orders_clean, order_items_clean, dim_distributor_hist, regions",
        question="""dim_distributor_hist menyimpan riwayat region distributor (SCD Type 2, valid_to
eksklusif). Hitung revenue per region per tahun (2024 dan 2025) memakai region distributor
PADA SAAT order terjadi, bukan region saat ini. Gunakan definisi revenue standar.""",
        columns="region_id, region_name, year (INTEGER), revenue (2 desimal)",
        order="year ASC, region_id ASC",
    ),
    dict(
        id="s23", title="Query lambat 1: correlated subquery", level="sulit", priority=False,
        tables="orders_clean, order_items_clean",
        question="""Query di bawah mencari order COMPLETED tahun 2025 yang nilainya lebih dari 2 kali
rata-rata nilai order distributor yang sama. Hasilnya benar, tetapi lambat karena subquery
dihitung ulang per baris dan order_items_clean di-scan berkali-kali.

    SELECT o.order_id, o.distributor_id, t.order_total
    FROM orders_clean o
    JOIN (SELECT order_id, SUM(line_amount) AS order_total
          FROM order_items_clean GROUP BY order_id) t USING (order_id)
    WHERE o.status = 'COMPLETED'
      AND o.order_date BETWEEN DATE '2025-01-01' AND DATE '2025-12-31'
      AND t.order_total > (
          SELECT 2 * AVG(t2.order_total)
          FROM orders_clean o2
          JOIN (SELECT order_id, SUM(line_amount) AS order_total
                FROM order_items_clean GROUP BY order_id) t2 USING (order_id)
          WHERE o2.distributor_id = o.distributor_id
            AND o2.status = 'COMPLETED'
            AND o2.order_date BETWEEN DATE '2025-01-01' AND DATE '2025-12-31')
    ORDER BY o.distributor_id, o.order_id;

Tulis ulang supaya: tidak ada subquery di WHERE atau SELECT, dan order_items_clean
hanya disebut SATU kali. Hasil harus identik.""",
        columns="order_id, distributor_id, order_total",
        order="distributor_id ASC, order_id ASC",
    ),
    dict(
        id="s24", title="Query lambat 2: DISTINCT penambal dan filter non-sargable", level="sulit", priority=False,
        tables="orders_clean, order_items_clean, products, distributors, regions",
        question="""Query di bawah menghasilkan revenue per region, segment, dan bulan untuk 2025.
Hasilnya benar, tetapi penuh anti-pattern.

    SELECT DISTINCT r.region_name, p.segment, strftime(o.order_date, '%Y-%m') AS month,
           SUM(oi.line_amount) OVER (
               PARTITION BY r.region_name, p.segment, strftime(o.order_date, '%Y-%m')) AS revenue
    FROM (SELECT * FROM order_items_clean ORDER BY order_item_id) oi
    JOIN (SELECT * FROM orders_clean ORDER BY order_date) o ON o.order_id = oi.order_id
    JOIN products p ON upper(trim(p.product_code)) = upper(trim(oi.product_code))
    JOIN distributors d ON d.distributor_id = o.distributor_id
    JOIN regions r ON r.region_id = d.region_id
    WHERE o.status = 'COMPLETED' AND strftime(o.order_date, '%Y') = '2025'
    ORDER BY 1, 2, 3;

Tulis ulang dengan aturan: tanpa SELECT DISTINCT, tanpa window function, tanpa ORDER BY di
dalam subquery, tanpa fungsi yang membungkus order_date di WHERE (filter harus sargable,
bisa dipakai untuk partition pruning), dan tanpa fungsi di kondisi JOIN ON
(order_items_clean.product_code sudah bersih). Hasil harus identik.""",
        columns="region_name, segment, month (VARCHAR 'YYYY-MM'), revenue",
        order="region_name ASC, segment ASC, month ASC",
    ),
    dict(
        id="s25", title="Query lambat 3: scan berulang", level="sulit", priority=False,
        tables="orders_clean, order_items_clean, products",
        question="""Query di bawah membuat ringkasan per segment. Setiap kolom dihitung di subquery
terpisah, sehingga tabel transaksi di-scan 4 kali.

    SELECT s.segment, a.rev_2024, b.rev_2025, c.orders_2025, e.avg_qty_2025
    FROM (SELECT DISTINCT segment FROM products) s
    LEFT JOIN (SELECT p.segment, SUM(oi.line_amount) AS rev_2024
               FROM order_items_clean oi JOIN orders_clean o USING (order_id)
               JOIN products p USING (product_code)
               WHERE o.status = 'COMPLETED'
                 AND o.order_date >= DATE '2024-01-01' AND o.order_date < DATE '2025-01-01'
               GROUP BY 1) a USING (segment)
    LEFT JOIN (SELECT p.segment, SUM(oi.line_amount) AS rev_2025
               FROM order_items_clean oi JOIN orders_clean o USING (order_id)
               JOIN products p USING (product_code)
               WHERE o.status = 'COMPLETED'
                 AND o.order_date >= DATE '2025-01-01' AND o.order_date < DATE '2026-01-01'
               GROUP BY 1) b USING (segment)
    LEFT JOIN (SELECT p.segment, COUNT(DISTINCT o.order_id) AS orders_2025
               FROM order_items_clean oi JOIN orders_clean o USING (order_id)
               JOIN products p USING (product_code)
               WHERE o.status = 'COMPLETED'
                 AND o.order_date >= DATE '2025-01-01' AND o.order_date < DATE '2026-01-01'
               GROUP BY 1) c USING (segment)
    LEFT JOIN (SELECT p.segment, AVG(oi.quantity) AS avg_qty_2025
               FROM order_items_clean oi JOIN orders_clean o USING (order_id)
               JOIN products p USING (product_code)
               WHERE o.status = 'COMPLETED'
                 AND o.order_date >= DATE '2025-01-01' AND o.order_date < DATE '2026-01-01'
               GROUP BY 1) e USING (segment)
    ORDER BY 1;

Tulis ulang supaya order_items_clean dan orders_clean masing-masing hanya disebut SATU kali
dan tidak ada UNION. Hasil harus identik.""",
        columns="segment, rev_2024, rev_2025, orders_2025, avg_qty_2025",
        order="segment ASC",
    ),
]

BY_ID = {q["id"]: q for q in QUESTIONS}
