"""Kunci jawaban DQ05."""

from __future__ import annotations

import statistics
from datetime import datetime, timedelta

import pandas as pd

from dq_base import CheckResult


def check_freshness(df: pd.DataFrame, ts_col: str, max_age: timedelta, now: datetime) -> CheckResult:
    ts = pd.to_datetime(df[ts_col], errors="coerce") if len(df) else pd.Series([], dtype="datetime64[ns]")
    latest = ts.max() if len(ts) else pd.NaT
    if pd.isna(latest):
        return CheckResult(f"freshness:{ts_col}", False, 1, len(df), {"latest": None, "age_hours": None})
    age = pd.Timestamp(now) - latest
    ok = age <= max_age
    return CheckResult(f"freshness:{ts_col}", bool(ok), 0 if ok else 1, len(df),
                       {"latest": latest.strftime("%Y-%m-%dT%H:%M:%S"),
                        "age_hours": round(age.total_seconds() / 3600, 2)})


def check_volume(today_count: int, history_counts: list[int], tolerance_pct: float = 30.0) -> CheckResult:
    if not history_counts:
        raise ValueError("history_counts kosong, tidak ada pembanding")
    expected = statistics.median(history_counts)
    dev = round((today_count - expected) / expected * 100, 2)
    ok = abs(dev) <= tolerance_pct
    return CheckResult("volume", ok, 0 if ok else 1, today_count,
                       {"expected": expected, "deviation_pct": dev})
