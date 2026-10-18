"""Kunci jawaban P01."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

NULL_MARKERS = ["", "NA", "N/A", "null", "NULL"]


def extract_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File sumber tidak ditemukan: {path}")
    # dtype=str mencegah tebakan tipe; keep_default_na=False supaya hanya NULL_MARKERS yang jadi NaN
    df = pd.read_csv(path, dtype=str, keep_default_na=False, na_values=NULL_MARKERS)
    df["_source_file"] = path.name
    return df
