"""
DQ05 | Freshness dan volume
Tingkat: SEDANG

SOAL
  1. check_freshness(df, ts_col, max_age, now) -> CheckResult
       Data dianggap segar kalau timestamp TERBARU di ts_col tidak lebih tua dari max_age
       dibanding `now`. ts_col bisa berupa string atau datetime. Nilai yang tidak bisa
       di-parse diabaikan.
         check        = f"freshness:{ts_col}"
         passed       = (now - latest) <= max_age. Kalau tidak ada timestamp valid sama
                        sekali (termasuk df kosong), passed = False.
         failed_rows  = 0 kalau lulus, 1 kalau gagal (freshness adalah cek level tabel)
         total_rows   = jumlah baris df
         details      = {"latest": latest dalam format ISO 'YYYY-MM-DDTHH:MM:SS' atau None,
                         "age_hours": umur dalam jam dibulatkan 2 desimal atau None}

  2. check_volume(today_count, history_counts, tolerance_pct=30.0) -> CheckResult
       Bandingkan jumlah baris hari ini dengan MEDIAN history_counts (jumlah baris hari-hari
       sebelumnya). Median dipakai karena tahan terhadap satu hari yang anomali.
         check        = "volume"
         deviation_pct= (today_count - median) / median * 100, dibulatkan 2 desimal
         passed       = abs(deviation_pct) <= tolerance_pct
         failed_rows  = 0 kalau lulus, 1 kalau gagal; total_rows = today_count
         details      = {"expected": median, "deviation_pct": deviation_pct}
       Kalau history_counts kosong, raise ValueError.

Uji     : task test-quality -- -k dq05
Petunjuk: task hint -- dq05
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

from dq_base import CheckResult


def check_freshness(df: pd.DataFrame, ts_col: str, max_age: timedelta, now: datetime) -> CheckResult:
    raise NotImplementedError


def check_volume(today_count: int, history_counts: list[int], tolerance_pct: float = 30.0) -> CheckResult:
    raise NotImplementedError
