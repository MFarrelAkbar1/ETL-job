"""Kunci jawaban DQ02."""

from __future__ import annotations

import pandas as pd

from dq_base import CheckResult


def check_unique(df: pd.DataFrame, key_cols: str | list[str]) -> CheckResult:
    cols = [key_cols] if isinstance(key_cols, str) else list(key_cols)
    null_mask = df[cols].isna().any(axis=1)
    keyed = df.loc[~null_mask, cols]
    # keep=False menandai SEMUA baris anggota duplikat, bukan hanya kemunculan kedua dst.
    dup_mask = keyed.duplicated(keep=False)
    dup_keys = keyed[dup_mask].drop_duplicates()
    sample = sorted(tuple(r) for r in dup_keys.itertuples(index=False))[:5]
    failed = int(dup_mask.sum() + null_mask.sum())
    return CheckResult("unique:" + ",".join(cols), failed == 0, failed, len(df),
                       {"duplicate_keys": int(len(dup_keys)), "null_keys": int(null_mask.sum()),
                        "sample": sample})
