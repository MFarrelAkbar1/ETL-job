"""Kunci jawaban P05."""

from __future__ import annotations

import numpy as np
import pandas as pd

REJECT_RULES = ["unit_price_null", "unit_price_non_positive", "quantity_null", "quantity_non_positive"]


def split_valid_invalid(items: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = items.copy()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

    conditions = [
        df["unit_price"].isna(),
        df["unit_price"] <= 0,
        df["quantity"].isna(),
        df["quantity"] <= 0,
    ]
    # np.select mengambil kondisi PERTAMA yang True, sesuai urutan aturan
    reason = np.select(conditions, REJECT_RULES, default="")
    bad = reason != ""

    valid = df[~bad].copy()
    valid["quantity"] = valid["quantity"].astype("int64")
    valid["unit_price"] = valid["unit_price"].astype("float64")
    rejected = df[bad].copy()
    rejected["reject_reason"] = reason[bad]
    return valid.reset_index(drop=True), rejected.reset_index(drop=True)
