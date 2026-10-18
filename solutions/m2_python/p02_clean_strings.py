"""Kunci jawaban P02."""

from __future__ import annotations

import numpy as np
import pandas as pd

STATUS_MAP = {
    "completed": "COMPLETED", "complete": "COMPLETED", "done": "COMPLETED",
    "cancelled": "CANCELLED", "canceled": "CANCELLED", "cancel": "CANCELLED",
    "pending": "PENDING", "waiting": "PENDING",
}


def normalize_product_code(s: pd.Series) -> pd.Series:
    out = s.astype("string").str.replace(r"\s+", "", regex=True).str.upper()
    out = out.replace("", pd.NA)
    return out.astype(object).where(out.notna(), np.nan)


def standardize_status(s: pd.Series) -> pd.Series:
    key = s.astype("string").str.strip().str.lower()
    return key.map(STATUS_MAP).fillna("UNKNOWN").astype(object)
