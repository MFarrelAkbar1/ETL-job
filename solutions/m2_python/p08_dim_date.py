"""Kunci jawaban P08."""

from __future__ import annotations

from datetime import date

import pandas as pd

MONTHS_ID = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus",
             "September", "Oktober", "November", "Desember"]
DAYS_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]


def build_dim_date(start: str | date, end: str | date) -> pd.DataFrame:
    s, e = pd.Timestamp(start), pd.Timestamp(end)
    if s > e:
        raise ValueError(f"start ({s.date()}) lebih besar dari end ({e.date()})")
    d = pd.Series(pd.date_range(s, e, freq="D"))
    dow = d.dt.dayofweek  # 0 = Senin
    return pd.DataFrame({
        "date_key": (d.dt.year * 10000 + d.dt.month * 100 + d.dt.day).astype("int64"),
        "date": d,
        "year": d.dt.year.astype(int),
        "quarter": d.dt.quarter.astype(int),
        "month": d.dt.month.astype(int),
        "day": d.dt.day.astype(int),
        # nama dari list sendiri, bukan strftime('%A'), supaya tidak tergantung locale
        "month_name": d.dt.month.map(lambda m: MONTHS_ID[m - 1]),
        "day_of_week": (dow + 1).astype(int),
        "day_name": dow.map(lambda i: DAYS_ID[i]),
        "week_of_year": d.dt.isocalendar().week.astype(int).to_numpy(),
        "is_weekend": dow >= 5,
        "is_month_end": d.dt.is_month_end,
    })
