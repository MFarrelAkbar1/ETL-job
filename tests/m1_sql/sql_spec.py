"""Spesifikasi penilaian per soal SQL.

ordered   : apakah urutan baris ikut dinilai
mistakes  : daftar (pesan, query_salah). Kalau hasil Anda SAMA PERSIS dengan hasil query
            salah ini, pesan khusus ditampilkan. Query di sini sengaja keliru.
static    : aturan struktur query (untuk soal "query lambat")
"""

REV_2025 = ("o.status = 'COMPLETED' AND o.order_date >= DATE '2025-01-01' "
            "AND o.order_date < DATE '2026-01-01'")

SPECS = {
    "s01": dict(ordered=True),
    "s02": dict(ordered=True, mistakes=[
        ("n_orders terlalu besar. Setelah JOIN ke order_items_clean, satu order muncul sebagai "
         "beberapa baris item. Yang dihitung adalah order, bukan baris.",
         f"""SELECT d.distributor_id, d.distributor_name, COUNT(*) AS n_orders, ROUND(SUM(oi.line_amount),2) AS revenue
             FROM orders_clean o JOIN distributors d ON d.distributor_id=o.distributor_id
             JOIN order_items_clean oi ON oi.order_id=o.order_id WHERE {REV_2025} GROUP BY ALL"""),
        ("Status order belum difilter. Definisi revenue standar hanya menghitung order COMPLETED.",
         """SELECT d.distributor_id, d.distributor_name, COUNT(DISTINCT o.order_id) AS n_orders, ROUND(SUM(oi.line_amount),2) AS revenue
             FROM orders_clean o JOIN distributors d ON d.distributor_id=o.distributor_id
             JOIN order_items_clean oi ON oi.order_id=o.order_id
             WHERE o.order_date >= DATE '2025-01-01' AND o.order_date < DATE '2026-01-01' GROUP BY ALL"""),
    ]),
    "s03": dict(ordered=True, mistakes=[
        ("Region tanpa distributor bernilai 1. COUNT(*) menghitung baris hasil LEFT JOIN, termasuk "
         "baris yang kolom kanannya NULL. Hitung kolom dari tabel kanan.",
         """SELECT r.region_id, r.region_name, COUNT(*) AS n_distributors,
                   COUNT(d.distributor_id) FILTER (WHERE d.is_active) AS n_active
             FROM regions r LEFT JOIN distributors d ON d.region_id=r.region_id GROUP BY ALL"""),
    ]),
    "s04": dict(ordered=True, mistakes=[
        ("Baru syarat revenue yang diterapkan. Syarat jumlah order juga harus ada di HAVING.",
         f"""SELECT o.distributor_id, COUNT(DISTINCT o.order_id) AS n_orders, ROUND(SUM(oi.line_amount),2) AS revenue
             FROM orders_clean o JOIN order_items_clean oi ON oi.order_id=o.order_id
             WHERE {REV_2025} AND o.distributor_id IS NOT NULL GROUP BY 1
             HAVING SUM(oi.line_amount) >= 1500000000"""),
        ("Syarat jumlah order Anda menghitung baris item, bukan order unik.",
         f"""SELECT o.distributor_id, COUNT(DISTINCT o.order_id) AS n_orders, ROUND(SUM(oi.line_amount),2) AS revenue
             FROM orders_clean o JOIN order_items_clean oi ON oi.order_id=o.order_id
             WHERE {REV_2025} AND o.distributor_id IS NOT NULL GROUP BY 1
             HAVING SUM(oi.line_amount) >= 1500000000 AND COUNT(*) >= 300"""),
    ]),
    "s05": dict(ordered=True),
    "s06": dict(ordered=True, mistakes=[
        ("Revenue Anda menghitung semua status. Revenue hanya untuk COMPLETED, sedangkan n_orders "
         "menghitung semua status. Pakai agregasi kondisional (FILTER atau CASE WHEN).",
         """SELECT o.distributor_id, COUNT(DISTINCT o.order_id) AS n_orders, ROUND(SUM(oi.line_amount),2) AS revenue
             FROM orders_clean o JOIN order_items_clean oi ON oi.order_id=o.order_id
             WHERE o.distributor_id IS NOT NULL AND o.distributor_id NOT IN (SELECT distributor_id FROM distributors)
             GROUP BY 1"""),
    ]),
    "s07": dict(ordered=True, mistakes=[
        ("Banyak baris item hilang. product_code di tabel mentah masih mengandung huruf kecil dan "
         "spasi, jadi tidak cocok dengan master saat JOIN.",
         """SELECT p.product_code, p.product_name, SUM(oi.quantity) AS total_qty, COUNT(*) AS n_lines
             FROM order_items oi JOIN products p ON p.product_code = oi.product_code
             WHERE p.segment='Farmasi' GROUP BY ALL"""),
        ("Kode sudah diseragamkan huruf besarnya, tapi spasi di depan/belakang belum dibuang.",
         """SELECT p.product_code, p.product_name, SUM(oi.quantity) AS total_qty, COUNT(*) AS n_lines
             FROM order_items oi JOIN products p ON p.product_code = UPPER(oi.product_code)
             WHERE p.segment='Farmasi' GROUP BY ALL"""),
        ("n_lines tidak menghitung baris dengan quantity NULL. COUNT(quantity) melewati NULL; "
         "soal meminta semua baris item dihitung.",
         """SELECT p.product_code, p.product_name, SUM(oi.quantity) AS total_qty, COUNT(oi.quantity) AS n_lines
             FROM order_items oi JOIN products p ON p.product_code = UPPER(TRIM(oi.product_code))
             WHERE p.segment='Farmasi' GROUP BY ALL"""),
    ]),
    "s08": dict(ordered=True),
    "s09": dict(ordered=True, mistakes=[
        ("gross_revenue terlalu besar karena fan-out: order_items_clean dan returns di-JOIN "
         "bersamaan ke orders, sehingga item terduplikasi untuk setiap return di order yang sama. "
         "Agregasikan masing-masing dulu, baru gabungkan.",
         f"""WITH x AS (SELECT d.region_id, SUM(oi.line_amount) g, COALESCE(SUM(r.refund_amount),0) f
             FROM orders_clean o JOIN distributors d ON d.distributor_id=o.distributor_id
             JOIN order_items_clean oi ON oi.order_id=o.order_id
             LEFT JOIN returns r ON r.order_id=o.order_id WHERE {REV_2025} GROUP BY 1)
             SELECT x.region_id, rg.region_name, ROUND(g,2) gross_revenue, ROUND(f,2) refund_amount,
                    ROUND(g-f,2) net_revenue, ROUND(f/g*100,2) return_rate_pct
             FROM x JOIN regions rg USING (region_id)"""),
    ]),
    "s10": dict(ordered=True, mistakes=[
        ("Hanya format 'YYYY-MM-DD' yang berhasil di-parse. Masih ada dua format lain.",
         """SELECT DATE_TRUNC('month', TRY_STRPTIME(order_date,'%Y-%m-%d'))::DATE AS order_month,
                   COUNT(DISTINCT order_id) AS n_orders FROM orders GROUP BY 1"""),
        ("n_orders terlalu besar: order_id duplikat di tabel mentah ikut terhitung. Hitung order unik.",
         """SELECT DATE_TRUNC('month', COALESCE(TRY_STRPTIME(order_date,'%Y-%m-%d'),TRY_STRPTIME(order_date,'%d/%m/%Y'),
                   TRY_STRPTIME(order_date,'%d-%b-%Y')))::DATE AS order_month, COUNT(*) AS n_orders FROM orders GROUP BY 1"""),
    ]),
    "s11": dict(ordered=True),
    "s12": dict(ordered=True),
    "s13": dict(ordered=True, mistakes=[
        ("Masih ada order_id duplikat. DISTINCT hanya membuang baris yang identik di SEMUA kolom, "
         "sedangkan versi lama sebuah order punya status dan updated_at yang berbeda.",
         """SELECT DISTINCT order_id, order_date, distributor_id, status, channel, updated_at FROM orders"""),
        ("Anda mengambil versi PALING LAMA. Urutkan updated_at dari yang terbaru.",
         """SELECT order_id, order_date, distributor_id, status, channel, updated_at FROM orders
             QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at) = 1"""),
    ]),
    "s14": dict(ordered=True),
    "s15": dict(ordered=True, mistakes=[
        ("Gap dihitung dari baris order, bukan tanggal unik. Kalau satu hari ada beberapa order, "
         "LEAD akan menghasilkan gap 0 dan gap yang sebenarnya bisa muncul dobel.",
         """WITH n AS (SELECT o.distributor_id, o.order_date,
                    LEAD(o.order_date) OVER (PARTITION BY o.distributor_id ORDER BY o.order_date) AS next_order_date
             FROM orders_clean o JOIN distributors d USING (distributor_id)
             WHERE o.order_date >= DATE '2025-01-01' AND o.order_date < DATE '2026-01-01')
             SELECT distributor_id, order_date, next_order_date, CAST(next_order_date-order_date AS INTEGER) gap_days
             FROM n WHERE next_order_date-order_date >= 21"""),
    ]),
    "s16": dict(ordered=True, mistakes=[
        ("running_revenue tidak di-reset di awal tahun. Tambahkan tahun ke PARTITION BY.",
         """WITH d AS (SELECT di.region_id, o.order_date, SUM(oi.line_amount) r FROM orders_clean o
             JOIN distributors di ON di.distributor_id=o.distributor_id JOIN order_items_clean oi ON oi.order_id=o.order_id
             WHERE o.status='COMPLETED' GROUP BY 1,2)
             SELECT region_id, order_date, ROUND(r,2) daily_revenue,
                    ROUND(SUM(r) OVER (PARTITION BY region_id ORDER BY order_date),2) running_revenue FROM d"""),
    ]),
    "s17": dict(ordered=True, mistakes=[
        ("Hari tanpa penjualan belum muncul. Buat date spine (deret tanggal lengkap) lalu LEFT JOIN, "
         "isi 0 untuk hari kosong.",
         """WITH d AS (SELECT o.order_date, SUM(oi.line_amount) r FROM orders_clean o JOIN order_items_clean oi USING (order_id)
             WHERE o.status='COMPLETED' AND o.distributor_id='D007' AND o.order_date BETWEEN DATE '2025-01-01' AND DATE '2025-03-31' GROUP BY 1)
             SELECT order_date, ROUND(r,2) daily_revenue,
                    ROUND(AVG(r) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW),2) ma_7d FROM d"""),
    ]),
    "s18": dict(ordered=True),
    "s19": dict(ordered=True, mistakes=[
        ("Tanggal yang hanya ada di salah satu tabel hilang. INNER/LEFT JOIN tidak cukup; pakai "
         "FULL OUTER JOIN setelah agregasi per sisi.",
         """WITH s AS (SELECT order_date, COUNT(*) n, SUM(amount) a FROM stg_sales GROUP BY 1),
                  t AS (SELECT order_date, COUNT(*) n, SUM(amount) a FROM dwh_sales GROUP BY 1)
             SELECT s.order_date, s.n src_rows, COALESCE(t.n,0) tgt_rows, ROUND(s.a,2) src_amount, ROUND(COALESCE(t.a,0),2) tgt_amount,
                    COALESCE(t.n,0)-s.n row_diff, ROUND(COALESCE(t.a,0)-s.a,2) amount_diff,
                    CASE WHEN COALESCE(t.n,0)=s.n AND ROUND(COALESCE(t.a,0)-s.a,2)=0 THEN 'OK' ELSE 'MISMATCH' END status
             FROM s LEFT JOIN t USING (order_date)"""),
    ]),
    "s20": dict(kind="dml", tables=["dim_product", "product_updates"],
                check_table="dim_product", order_by="product_id", idempotent=True),
    "s21": dict(kind="dml", tables=["dim_distributor_scd2", "distributor_snapshot"],
                check_table="dim_distributor_scd2", order_by="distributor_id, valid_from",
                exclude_cols=["distributor_sk"], unique_col="distributor_sk", idempotent=True),
    "s22": dict(ordered=True, mistakes=[
        ("Anda memakai region SAAT INI (is_current), bukan region pada tanggal order. "
         "JOIN harus memakai rentang valid_from <= order_date < valid_to.",
         """SELECT h.region_id, r.region_name, CAST(year(o.order_date) AS INTEGER) AS year, ROUND(SUM(oi.line_amount),2) revenue
             FROM orders_clean o JOIN order_items_clean oi USING (order_id)
             JOIN dim_distributor_hist h ON h.distributor_id=o.distributor_id AND h.is_current
             JOIN regions r ON r.region_id=h.region_id WHERE o.status='COMPLETED' GROUP BY ALL"""),
        ("Batas valid_to diperlakukan inklusif (<=), sehingga order tepat di tanggal perpindahan "
         "terhitung dua kali. Konvensinya valid_to eksklusif.",
         """SELECT h.region_id, r.region_name, CAST(year(o.order_date) AS INTEGER) AS year, ROUND(SUM(oi.line_amount),2) revenue
             FROM orders_clean o JOIN order_items_clean oi USING (order_id)
             JOIN dim_distributor_hist h ON h.distributor_id=o.distributor_id AND o.order_date BETWEEN h.valid_from AND h.valid_to
             JOIN regions r ON r.region_id=h.region_id WHERE o.status='COMPLETED' GROUP BY ALL"""),
    ]),
    "s23": dict(ordered=True,
                static=dict(no_subquery_in_where_select=True, max_table_refs={"order_items_clean": 1}),
                mistakes=[
        ("Ada order dengan distributor_id NULL yang ikut masuk. Di query asli, kondisi "
         "o2.distributor_id = o.distributor_id tidak pernah TRUE untuk NULL, sedangkan PARTITION BY "
         "mengelompokkan semua NULL menjadi satu grup.",
         """WITH t AS (SELECT o.order_id, o.distributor_id, SUM(oi.line_amount) order_total FROM orders_clean o
             JOIN order_items_clean oi USING (order_id) WHERE o.status='COMPLETED'
             AND o.order_date BETWEEN DATE '2025-01-01' AND DATE '2025-12-31' GROUP BY 1,2)
             SELECT * FROM t QUALIFY order_total > 2*AVG(order_total) OVER (PARTITION BY distributor_id)"""),
    ]),
    "s24": dict(ordered=True, static=dict(
        no_select_distinct=True, no_window=True, no_order_in_subquery=True,
        sargable_column="order_date", no_func_in_join=True)),
    "s25": dict(ordered=True, static=dict(
        max_table_refs={"order_items_clean": 1, "orders_clean": 1}, no_union=True)),
}
