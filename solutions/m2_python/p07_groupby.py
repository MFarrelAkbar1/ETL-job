"""Kunci jawaban P07."""

from __future__ import annotations

import pandas as pd


def monthly_revenue_by_segment(df: pd.DataFrame) -> pd.DataFrame:
    d = df[df["status"] == "COMPLETED"].copy()
    d["month"] = pd.to_datetime(d["order_date"]).dt.strftime("%Y-%m")
    out = (d.groupby(["month", "segment"], as_index=False)
             .agg(revenue=("line_amount", "sum"), n_orders=("order_id", "nunique")))
    out["avg_order_value"] = (out["revenue"] / out["n_orders"]).round(2)
    out["revenue"] = out["revenue"].round(2)
    out["n_orders"] = out["n_orders"].astype(int)
    return out.sort_values(["month", "segment"]).reset_index(drop=True)


def top_n_per_group(df: pd.DataFrame, group_col: str, value_col: str, n: int = 3) -> pd.DataFrame:
    d = df.sort_values([group_col, value_col], ascending=[True, False], kind="stable")
    d = d.groupby(group_col, sort=False).head(n).copy()
    d["rank"] = d.groupby(group_col).cumcount() + 1
    return d.reset_index(drop=True)
