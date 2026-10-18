"""Kunci jawaban P03."""

from __future__ import annotations

from datetime import datetime

import pandas as pd

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%b-%Y"]


def parse_mixed_dates(s: pd.Series) -> pd.Series:
    txt = s.astype("string").str.strip()
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    for fmt in DATE_FORMATS:
        # format eksplisit + errors="coerce": gagal parse jadi NaT, bukan tebakan
        out = out.fillna(pd.to_datetime(txt, format=fmt, errors="coerce"))
    return out


def detect_format(value: str | None) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    for fmt in DATE_FORMATS:
        try:
            datetime.strptime(str(value).strip(), fmt)
            return fmt
        except ValueError:
            continue
    return None
