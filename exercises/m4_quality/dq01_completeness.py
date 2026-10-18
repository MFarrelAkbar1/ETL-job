"""
DQ01 | Completeness
Tingkat: MUDAH

SOAL
  check_completeness(df, columns, max_null_rate=0.0) -> list[CheckResult]

  Untuk SETIAP kolom di `columns` (urutan sama), buat satu CheckResult:
    check        = f"not_null:{kolom}"
    failed_rows  = jumlah nilai yang dianggap kosong
    total_rows   = jumlah baris df
    passed       = (failed_rows / total_rows) <= max_null_rate
                   (df kosong dianggap lulus)
    details      = {"null_rate": failed_rows / total_rows dibulatkan 4 desimal}

  Nilai yang dianggap kosong: None, NaN, NaT, dan string yang kosong atau hanya berisi spasi.
  String 'N/A' atau '0' BUKAN kosong (itu urusan pengecekan validity).
  Kalau kolom tidak ada di df, raise KeyError yang pesannya menyebut nama kolom.

Uji     : task test-quality -- -k dq01
Petunjuk: task hint -- dq01
"""

from __future__ import annotations

import pandas as pd

from dq_base import CheckResult


def check_completeness(df: pd.DataFrame, columns: list[str], max_null_rate: float = 0.0) -> list[CheckResult]:
    raise NotImplementedError
