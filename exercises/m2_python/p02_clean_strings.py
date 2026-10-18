"""
P02 | Transform: membersihkan kolom teks
Tingkat: MUDAH

SOAL
  1. normalize_product_code(s)
     Di data mentah, kode produk ditulis 'prd-0044 ', ' PRD-0063 ', 'Prd - 0001'.
     Kembalikan Series baru dengan aturan:
       - huruf besar semua
       - SEMUA whitespace dibuang (di tepi maupun di tengah)
       - string yang kosong setelah dibersihkan menjadi NaN
       - NaN tetap NaN
     Index Series harus sama dengan input. Jangan memakai loop Python per baris.

  2. standardize_status(s)
     Petakan variasi status ke nilai baku. Perbandingan tidak peka huruf besar kecil dan
     spasi di tepi.
       'COMPLETED' <- completed, complete, done
       'CANCELLED' <- cancelled, canceled, cancel
       'PENDING'   <- pending, waiting
     Nilai lain, termasuk NaN, menjadi 'UNKNOWN'.

Uji     : task test-python -- -k p02
Petunjuk: task hint -- p02
"""

from __future__ import annotations

import pandas as pd


def normalize_product_code(s: pd.Series) -> pd.Series:
    raise NotImplementedError


def standardize_status(s: pd.Series) -> pd.Series:
    raise NotImplementedError
