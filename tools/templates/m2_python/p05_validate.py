"""
P05 | Validate: memisahkan baris valid dan baris ditolak
Tingkat: SEDANG

SOAL
  split_valid_invalid(items) -> (valid, rejected)

  Input adalah order_items hasil extract (semua kolom string). Kolom penting: quantity,
  unit_price.

  Langkah:
  1. Ubah quantity dan unit_price menjadi angka. Teks yang bukan angka dianggap NULL.
  2. Tentukan alasan penolakan per baris. Aturan diperiksa BERURUTAN, ambil yang pertama cocok:
       'unit_price_null'          unit_price NULL
       'unit_price_non_positive'  unit_price <= 0
       'quantity_null'            quantity NULL
       'quantity_non_positive'    quantity <= 0
  3. valid    : baris tanpa alasan penolakan. quantity bertipe int64, unit_price float64.
                Tidak ada kolom reject_reason.
     rejected : baris yang ditolak, dengan kolom tambahan reject_reason.
     Keduanya mempertahankan urutan baris input dan index di-reset.
  4. Tidak boleh ada baris yang hilang: len(valid) + len(rejected) == len(items).

Uji     : task test-python -- -k p05
Petunjuk: task hint -- p05
"""

from __future__ import annotations

import pandas as pd

REJECT_RULES = ["unit_price_null", "unit_price_non_positive", "quantity_null", "quantity_non_positive"]


def split_valid_invalid(items: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    raise NotImplementedError
