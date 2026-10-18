"""
P08 | Transform: membangun dimensi tanggal
Tingkat: SEDANG

SOAL
  build_dim_date(start, end) -> DataFrame, satu baris per tanggal dari start sampai end
  (inklusif). start dan end berupa string 'YYYY-MM-DD' atau date. Kalau start > end,
  raise ValueError.

  Kolom (urut):
    date_key      int YYYYMMDD, contoh 20250314
    date          datetime64[ns]
    year, quarter, month, day     int
    month_name    nama bulan Bahasa Indonesia: Januari, Februari, Maret, April, Mei, Juni,
                  Juli, Agustus, September, Oktober, November, Desember
    day_of_week   1 = Senin ... 7 = Minggu (ISO)
    day_name      Senin, Selasa, Rabu, Kamis, Jumat, Sabtu, Minggu
    week_of_year  minggu ISO (int)
    is_weekend    bool, TRUE untuk Sabtu dan Minggu
    is_month_end  bool

  Jangan bergantung pada locale sistem untuk nama hari/bulan.

Uji     : task test-python -- -k p08
Petunjuk: task hint -- p08
"""

from __future__ import annotations

from datetime import date

import pandas as pd

MONTHS_ID = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus",
             "September", "Oktober", "November", "Desember"]
DAYS_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]


def build_dim_date(start: str | date, end: str | date) -> pd.DataFrame:
    raise NotImplementedError
