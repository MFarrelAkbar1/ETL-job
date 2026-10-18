"""
P04 | Transform: deduplikasi, ambil versi terbaru
Tingkat: SEDANG

SOAL
  1. dedup_latest(df, key="order_id", ts_col="updated_at") -> DataFrame
       - satu baris per key, yaitu baris dengan ts_col paling baru
       - ts_col bisa berupa string; bandingkan sebagai waktu, bukan sebagai teks
       - kalau ts_col sama (seri), ambil baris yang muncul PALING AKHIR di input
       - kolom dan tipe kolom output sama dengan input (ts_col tidak berubah tipe)
       - hasil diurutkan berdasarkan key, index di-reset (0..n-1)
       - jangan mengubah DataFrame input

  2. duplicate_report(df, key) -> dict dengan kunci:
       n_rows            jumlah baris
       n_unique_keys     jumlah key unik
       n_duplicate_rows  jumlah baris yang akan dibuang oleh deduplikasi
       n_keys_with_dups  jumlah key yang muncul lebih dari sekali

Uji     : task test-python -- -k p04
Petunjuk: task hint -- p04
"""

from __future__ import annotations

import pandas as pd


def dedup_latest(df: pd.DataFrame, key: str = "order_id", ts_col: str = "updated_at") -> pd.DataFrame:
    raise NotImplementedError


def duplicate_report(df: pd.DataFrame, key: str) -> dict:
    raise NotImplementedError
