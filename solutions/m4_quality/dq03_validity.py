"""Kunci jawaban DQ03."""

from __future__ import annotations

import re
from typing import Iterable

import pandas as pd

from dq_base import CheckResult


def check_range(df: pd.DataFrame, col: str, min_value: float | None = None,
                max_value: float | None = None, inclusive: bool = True) -> CheckResult:
    vals = df[col].dropna()
    num = pd.to_numeric(vals, errors="coerce")
    bad = num.isna()  # teks yang bukan angka
    if min_value is not None:
        bad |= (num < min_value) if inclusive else (num <= min_value)
    if max_value is not None:
        bad |= (num > max_value) if inclusive else (num >= max_value)
    valid_num = num.dropna()
    details = {"min_found": float(valid_num.min()) if len(valid_num) else None,
               "max_found": float(valid_num.max()) if len(valid_num) else None}
    failed = int(bad.sum())
    return CheckResult(f"range:{col}", failed == 0, failed, int(len(vals)), details)


def check_allowed_values(df: pd.DataFrame, col: str, allowed: Iterable[str],
                         case_sensitive: bool = True) -> CheckResult:
    vals = df[col].dropna().astype(str)
    allowed = list(allowed)
    if case_sensitive:
        bad = ~vals.isin(allowed)
    else:
        bad = ~vals.str.lower().isin([a.lower() for a in allowed])
    unexpected = sorted(vals[bad].unique().tolist())[:10]
    failed = int(bad.sum())
    return CheckResult(f"accepted_values:{col}", failed == 0, failed, int(len(vals)),
                       {"unexpected": unexpected})


def check_regex(df: pd.DataFrame, col: str, pattern: str) -> CheckResult:
    vals = df[col].dropna().astype(str)
    rx = re.compile(pattern)
    bad = ~vals.map(lambda v: rx.fullmatch(v) is not None)
    failed = int(bad.sum())
    return CheckResult(f"regex:{col}", failed == 0, failed, int(len(vals)),
                       {"sample": sorted(vals[bad].unique().tolist())[:5]})
