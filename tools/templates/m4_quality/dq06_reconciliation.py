"""
DQ06 | Rekonsiliasi sumber vs target
Tingkat: SEDANG

SOAL
  reconcile(source, target, key, amount_col, tolerance=0.01) -> (CheckResult, DataFrame)

  Versi pandas dari soal SQL S19, tetapi di level key (misalnya order_id).
  1. Agregasikan masing-masing sisi per key DULU: jumlah amount_col (baris dengan key sama
     dijumlahkan, karena target bisa punya baris dobel).
  2. Bandingkan kedua sisi. Setiap key masuk salah satu status:
       'ONLY_SOURCE'  ada di source, tidak ada di target
       'ONLY_TARGET'  ada di target, tidak ada di source
       'AMOUNT_DIFF'  ada di keduanya, abs(selisih) > tolerance
       (key yang cocok tidak dimasukkan ke DataFrame selisih)
  3. DataFrame selisih: kolom [key, 'status', 'source_amount', 'target_amount'],
     sisi yang tidak ada bernilai NaN, diurutkan berdasarkan key, index di-reset.
  4. CheckResult:
       check        = f"reconcile:{key}"
       failed_rows  = jumlah key bermasalah (baris DataFrame selisih)
       total_rows   = jumlah key unik gabungan kedua sisi
       passed       = failed_rows == 0
       details      = {"only_source": n, "only_target": n, "amount_diff": n,
                       "source_total": total amount source (2 desimal),
                       "target_total": total amount target (2 desimal)}

Uji     : task test-quality -- -k dq06
Petunjuk: task hint -- dq06
"""

from __future__ import annotations

import pandas as pd

from dq_base import CheckResult


def reconcile(source: pd.DataFrame, target: pd.DataFrame, key: str, amount_col: str,
              tolerance: float = 0.01) -> tuple[CheckResult, pd.DataFrame]:
    raise NotImplementedError
