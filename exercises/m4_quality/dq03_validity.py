"""
DQ03 | Validity
Tingkat: SEDANG

SOAL
  Tiga pengecekan validity. Pada ketiganya, nilai NULL DIABAIKAN (tidak dihitung gagal,
  dan tidak ikut total_rows), karena NULL sudah ditangani pengecekan completeness.
  total_rows = jumlah nilai yang tidak NULL. passed = failed_rows == 0.

  1. check_range(df, col, min_value=None, max_value=None, inclusive=True)
       check = f"range:{col}"
       Nilai di luar [min_value, max_value] gagal (batas None berarti tidak dibatasi).
       inclusive=False berarti batas itu sendiri juga gagal.
       Nilai yang tidak bisa diubah menjadi angka juga gagal.
       details = {"min_found": nilai numerik terkecil, "max_found": terbesar}
                 (None kalau tidak ada nilai numerik)

  2. check_allowed_values(df, col, allowed, case_sensitive=True)
       check = f"accepted_values:{col}"
       Kalau case_sensitive=False, 'completed' dianggap sama dengan 'COMPLETED'.
       Spasi di tepi TIDAK diabaikan: ' COMPLETED' gagal.
       details = {"unexpected": list nilai asli unik yang gagal, terurut, maksimal 10}

  3. check_regex(df, col, pattern)
       check = f"regex:{col}"
       Nilai (sebagai string) harus cocok PENUH dengan pattern, bukan sebagian.
       details = {"sample": list sampai 5 nilai unik pertama yang gagal, terurut}

Uji     : task test-quality -- -k dq03
Petunjuk: task hint -- dq03
"""

from __future__ import annotations

from typing import Iterable

import pandas as pd

from dq_base import CheckResult


def check_range(df: pd.DataFrame, col: str, min_value: float | None = None,
                max_value: float | None = None, inclusive: bool = True) -> CheckResult:
    raise NotImplementedError


def check_allowed_values(df: pd.DataFrame, col: str, allowed: Iterable[str],
                         case_sensitive: bool = True) -> CheckResult:
    raise NotImplementedError


def check_regex(df: pd.DataFrame, col: str, pattern: str) -> CheckResult:
    raise NotImplementedError
