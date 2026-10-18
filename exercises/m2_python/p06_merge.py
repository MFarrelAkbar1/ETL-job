"""
P06 | Transform: merge yang aman
Tingkat: SEDANG

SOAL
  1. enrich_items(items, products) -> DataFrame
       - normalisasi product_code di items DAN products (aturan sama dengan P02:
         huruf besar, tanpa whitespace). Boleh import dari p02_clean_strings.
       - kalau products punya product_code duplikat (setelah normalisasi), raise ValueError
         yang pesannya mengandung kata 'duplikat'
       - tambahkan kolom product_name, segment, category dari products
       - item dengan kode yang tidak ada di master tetap dipertahankan:
         product_name NaN, segment 'UNKNOWN', category 'UNKNOWN'
       - jumlah dan urutan baris HARUS sama dengan items (merge tidak boleh menggandakan baris)
       - kolom product_code di output berisi kode yang sudah dinormalisasi

  2. attach_orders(items, orders) -> (DataFrame, int)
       - inner join items ke orders lewat order_id, tambahkan kolom order_date,
         distributor_id, status dari orders
       - kalau orders punya order_id duplikat, raise ValueError (harus dedup dulu)
       - kembalikan juga jumlah baris item yang terbuang karena order_id-nya tidak ada di orders
       - urutan baris items dipertahankan, index di-reset

Uji     : task test-python -- -k p06
Petunjuk: task hint -- p06
"""

from __future__ import annotations

import pandas as pd


def enrich_items(items: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError


def attach_orders(items: pd.DataFrame, orders: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    raise NotImplementedError
