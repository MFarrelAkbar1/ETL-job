"""Kunci jawaban DQ04."""

from __future__ import annotations

import pandas as pd

from dq_base import CheckResult


def check_foreign_key(child: pd.DataFrame, child_col: str, parent: pd.DataFrame, parent_col: str,
                      allow_null: bool = True) -> CheckResult:
    vals = child[child_col]
    null_mask = vals.isna()
    orphan_mask = ~null_mask & ~vals.isin(set(parent[parent_col].dropna()))
    failed = int(orphan_mask.sum() + (0 if allow_null else null_mask.sum()))
    orphans = sorted(vals[orphan_mask].unique().tolist())
    return CheckResult(f"relationship:{child_col}->{parent_col}", failed == 0, failed, len(child),
                       {"n_orphan_values": len(orphans), "orphan_values": orphans[:20],
                        "null_rows": int(null_mask.sum())})
