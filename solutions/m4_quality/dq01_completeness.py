"""Kunci jawaban DQ01."""

from __future__ import annotations

import pandas as pd

from dq_base import CheckResult


def is_blank(s: pd.Series) -> pd.Series:
    """True untuk None/NaN/NaT dan string kosong atau hanya spasi."""
    blank_str = s.map(lambda v: isinstance(v, str) and v.strip() == "")
    return s.isna() | blank_str


def check_completeness(df: pd.DataFrame, columns: list[str], max_null_rate: float = 0.0) -> list[CheckResult]:
    out = []
    n = len(df)
    for col in columns:
        if col not in df.columns:
            raise KeyError(f"Kolom tidak ada: {col}")
        failed = int(is_blank(df[col]).sum())
        rate = failed / n if n else 0.0
        out.append(CheckResult(f"not_null:{col}", rate <= max_null_rate, failed, n,
                               {"null_rate": round(rate, 4)}))
    return out
