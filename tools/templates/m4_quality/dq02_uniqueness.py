"""
DQ02 | Uniqueness
Tingkat: MUDAH

SOAL
  check_unique(df, key_cols) -> CheckResult

  key_cols bisa string (satu kolom) atau list (composite key).
    check        = "unique:" + nama kolom digabung koma, contoh "unique:order_id,line_no"
    failed_rows  = jumlah SEMUA baris yang key-nya muncul lebih dari sekali
                   (kalau order A muncul 3 kali, ketiganya dihitung) DITAMBAH baris yang
                   salah satu kolom key-nya NULL
    total_rows   = jumlah baris df
    passed       = failed_rows == 0
    details      = {
        "duplicate_keys": jumlah key unik yang punya duplikat (key NULL tidak ikut),
        "null_keys":      jumlah baris dengan key NULL,
        "sample":         sampai 5 key duplikat pertama setelah diurutkan, sebagai list of
                          tuple (selalu tuple, juga untuk key satu kolom)
    }

Uji     : task test-quality -- -k dq02
Petunjuk: task hint -- dq02
"""

from __future__ import annotations

import pandas as pd

from dq_base import CheckResult


def check_unique(df: pd.DataFrame, key_cols: str | list[str]) -> CheckResult:
    raise NotImplementedError
