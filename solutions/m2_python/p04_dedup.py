"""Kunci jawaban P04."""

from __future__ import annotations

import pandas as pd


def dedup_latest(df: pd.DataFrame, key: str = "order_id", ts_col: str = "updated_at") -> pd.DataFrame:
    tmp = df.assign(_ts=pd.to_datetime(df[ts_col]), _pos=range(len(df)))
    # urut waktu lalu posisi: baris terakhir per key adalah yang terbaru, seri dimenangkan yang paling akhir
    tmp = tmp.sort_values(["_ts", "_pos"], kind="stable")
    tmp = tmp.drop_duplicates(subset=key, keep="last")
    tmp = tmp.sort_values(key, kind="stable").drop(columns=["_ts", "_pos"])
    return tmp.reset_index(drop=True)


def duplicate_report(df: pd.DataFrame, key: str) -> dict:
    counts = df[key].value_counts(dropna=False)
    return {
        "n_rows": int(len(df)),
        "n_unique_keys": int(counts.size),
        "n_duplicate_rows": int(len(df) - counts.size),
        "n_keys_with_dups": int((counts > 1).sum()),
    }
