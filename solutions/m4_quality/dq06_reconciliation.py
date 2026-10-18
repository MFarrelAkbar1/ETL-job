"""Kunci jawaban DQ06."""

from __future__ import annotations

import numpy as np
import pandas as pd

from dq_base import CheckResult


def reconcile(source: pd.DataFrame, target: pd.DataFrame, key: str, amount_col: str,
              tolerance: float = 0.01) -> tuple[CheckResult, pd.DataFrame]:
    s = source.groupby(key, as_index=False)[amount_col].sum().rename(columns={amount_col: "source_amount"})
    t = target.groupby(key, as_index=False)[amount_col].sum().rename(columns={amount_col: "target_amount"})
    j = s.merge(t, on=key, how="outer", indicator=True)
    status = np.select(
        [j["_merge"] == "left_only", j["_merge"] == "right_only",
         (j["source_amount"] - j["target_amount"]).abs() > tolerance],
        ["ONLY_SOURCE", "ONLY_TARGET", "AMOUNT_DIFF"], default="")
    j["status"] = status
    diff = (j[j["status"] != ""][[key, "status", "source_amount", "target_amount"]]
            .sort_values(key).reset_index(drop=True))
    counts = diff["status"].value_counts()
    details = {"only_source": int(counts.get("ONLY_SOURCE", 0)),
               "only_target": int(counts.get("ONLY_TARGET", 0)),
               "amount_diff": int(counts.get("AMOUNT_DIFF", 0)),
               "source_total": round(float(source[amount_col].sum()), 2),
               "target_total": round(float(target[amount_col].sum()), 2)}
    res = CheckResult(f"reconcile:{key}", len(diff) == 0, int(len(diff)), int(len(j)), details)
    return res, diff
