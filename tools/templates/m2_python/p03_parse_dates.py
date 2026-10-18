"""
P03 | Transform: konversi tanggal dengan format campur
Tingkat: SEDANG

SOAL
  Kolom order_date mentah memakai tiga format: '%Y-%m-%d', '%d/%m/%Y', '%d-%b-%Y'
  (contoh: '2025-03-14', '14/03/2025', '14-Mar-2025').

  1. parse_mixed_dates(s) -> Series bertipe datetime64[ns]
       - coba ketiga format secara eksplisit (JANGAN pakai tebakan otomatis atau dayfirst)
       - '03/04/2025' berarti 3 April 2025
       - nilai yang tidak cocok dengan format mana pun, tanggal mustahil ('2025-02-30'),
         atau NaN menjadi NaT
       - spasi di tepi diabaikan
       - index sama dengan input

  2. detect_format(value) -> str | None
       Kembalikan string format yang cocok untuk satu nilai (salah satu dari DATE_FORMATS),
       atau None kalau tidak ada yang cocok. Berguna untuk profiling data.

Uji     : task test-python -- -k p03
Petunjuk: task hint -- p03
"""

from __future__ import annotations

import pandas as pd

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%b-%Y"]


def parse_mixed_dates(s: pd.Series) -> pd.Series:
    raise NotImplementedError


def detect_format(value: str | None) -> str | None:
    raise NotImplementedError
