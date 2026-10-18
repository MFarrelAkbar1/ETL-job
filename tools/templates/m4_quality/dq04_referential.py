"""
DQ04 | Referential integrity
Tingkat: MUDAH

SOAL
  check_foreign_key(child, child_col, parent, parent_col, allow_null=True) -> CheckResult

  Setiap nilai child[child_col] harus ada di parent[parent_col].
    check        = f"relationship:{child_col}->{parent_col}"
    failed_rows  = jumlah baris child yang nilainya tidak ada di parent (orphan).
                   Kalau allow_null=False, baris dengan child_col NULL juga gagal.
                   Kalau allow_null=True, baris NULL tidak gagal.
    total_rows   = jumlah baris child
    passed       = failed_rows == 0
    details      = {
        "n_orphan_values": jumlah nilai orphan UNIK (NULL tidak termasuk),
        "orphan_values":   list nilai orphan unik terurut, maksimal 20,
        "null_rows":       jumlah baris child dengan nilai NULL
    }

  Perbandingan persis (case sensitive). Normalisasi adalah tugas transform, bukan tugas check.

Uji     : task test-quality -- -k dq04
Petunjuk: task hint -- dq04
"""

from __future__ import annotations

import pandas as pd

from dq_base import CheckResult


def check_foreign_key(child: pd.DataFrame, child_col: str, parent: pd.DataFrame, parent_col: str,
                      allow_null: bool = True) -> CheckResult:
    raise NotImplementedError
