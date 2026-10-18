"""
DQ08 | Audit data mentah perusahaan
Tingkat: SULIT

SOAL
  audit_raw(raw_dir) -> DataFrame laporan

  Jalankan RULES di bawah terhadap CSV mentah di raw_dir (orders.csv, order_items.csv,
  products.csv, distributors.csv) memakai run_suite dari DQ07, lalu kembalikan laporannya.

  Hal yang harus Anda putuskan sendiri dengan benar:
  - Baca CSV sebagai string (seperti P01 di Modul 2), supaya validity diuji pada nilai asli,
    bukan nilai yang sudah ditebak pandas. Hanya '' (sel kosong) yang dianggap NULL.
  - Tambahkan kolom turunan yang dibutuhkan RULES sebelum menjalankan suite:
      orders.order_date_valid : 'Y' kalau order_date bisa di-parse dengan salah satu dari tiga
                                format (lihat P03), selain itu 'N' (termasuk NULL)
  - Kolom angka (unit_price, quantity) diperiksa dengan check range; nilai teks yang bukan
    angka otomatis gagal di check_range.

  Setelah lulus, baca laporannya dan jawab untuk diri sendiri: pengecekan mana yang
  seharusnya memblokir pipeline, dan mana cukup peringatan?

Uji     : task test-quality -- -k dq08
Petunjuk: task hint -- dq08
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RULES = [
    {"table": "orders", "check": "not_null", "column": "order_id"},
    {"table": "orders", "check": "unique", "columns": ["order_id"], "severity": "warn"},
    {"table": "orders", "check": "not_null", "column": "distributor_id", "severity": "warn"},
    {"table": "orders", "check": "accepted_values", "column": "status",
     "values": ["COMPLETED", "CANCELLED", "PENDING"]},
    {"table": "orders", "check": "accepted_values", "column": "order_date_valid", "values": ["Y"]},
    {"table": "orders", "check": "relationship", "column": "distributor_id",
     "to": "distributors", "field": "distributor_id", "severity": "warn"},
    {"table": "order_items", "check": "unique", "columns": ["order_item_id"]},
    {"table": "order_items", "check": "range", "column": "unit_price", "min": 0.01},
    {"table": "order_items", "check": "not_null", "column": "quantity"},
    {"table": "order_items", "check": "range", "column": "quantity", "min": 1},
    {"table": "order_items", "check": "relationship", "column": "product_code",
     "to": "products", "field": "product_code"},
    {"table": "order_items", "check": "relationship", "column": "order_id",
     "to": "orders", "field": "order_id"},
    {"table": "products", "check": "unique", "columns": ["product_code"]},
    {"table": "distributors", "check": "not_null", "column": "city", "severity": "warn"},
]


def audit_raw(raw_dir: str | Path) -> pd.DataFrame:
    raise NotImplementedError
