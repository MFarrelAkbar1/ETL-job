"""
P12 | Mini ETL lengkap: CSV kotor ke star schema
Tingkat: SULIT

SOAL
  run_etl(raw_dir, db_path) -> dict

  Baca CSV di raw_dir (orders.csv, order_items.csv, products.csv, distributors.csv,
  regions.csv), bersihkan, lalu tulis star schema ke DuckDB di db_path. Anda boleh (dan
  disarankan) memakai fungsi dari latihan P01 sampai P11 dengan import biasa, contoh:
      from p03_parse_dates import parse_mixed_dates

  ATURAN TRANSFORMASI
  1. orders     : deduplikasi per order_id, ambil updated_at terbaru. Order yang order_date-nya
                  tidak bisa di-parse (3 format seperti P03) DITOLAK.
  2. order_items: product_code dinormalisasi (huruf besar, tanpa whitespace). Setiap item
                  diperiksa berurutan, alasan pertama yang cocok dipakai:
                    'order_rejected'           order_id tidak ada di orders hasil langkah 1
                    'unit_price_null'          (aturan P05)
                    'unit_price_non_positive'
                    'quantity_null'
                    'quantity_non_positive'
                    'unknown_product'          product_code tidak ada di master products
  3. distributor_id yang NULL atau tidak ada di master (orphan) dipetakan ke anggota
     'unknown' di dim_distributor (distributor_key = -1). Fakta TIDAK dibuang.

  TABEL OUTPUT (mode replace, jalankan dua kali hasilnya harus sama)
  dim_product     : product_key (1..n urut product_id), product_id, product_code,
                    product_name, segment, category, brand
  dim_distributor : distributor_key (1..n urut distributor_id), distributor_id,
                    distributor_name, distributor_type, region_id, region_name, city
                    city NULL diisi 'UNKNOWN'.
                    Ditambah satu baris unknown: distributor_key = -1 dan semua kolom
                    teks = 'UNKNOWN'.
  dim_date        : kolom sama dengan P08, dari tanggal order terkecil sampai terbesar di
                    fact_sales, tanpa celah.
  fact_sales      : grain = satu baris per order_item_id yang lolos.
                    order_item_id, order_id, date_key, product_key, distributor_key,
                    quantity (int), unit_price, line_amount (= quantity * unit_price), status
                    Semua status order ikut (analis yang memfilter COMPLETED).
  rejected_order_items : order_item_id, order_id, reject_reason

  Return dict:
    fact_rows, rejected_rows, orders_after_dedup, orders_rejected

Uji     : task test-python -- -k p12   (memakai data/raw hasil task setup)
Petunjuk: task hint -- p12
"""

from __future__ import annotations

from pathlib import Path


def run_etl(raw_dir: str | Path, db_path: str | Path) -> dict:
    raise NotImplementedError
