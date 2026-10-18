"""Kunci jawaban ICE05."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
from pyiceberg.table import Table


def _sorted(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values("order_id").reset_index(drop=True)


def read_snapshot(table: Table, snapshot_id: int) -> pd.DataFrame:
    return _sorted(table.scan(snapshot_id=snapshot_id).to_pandas())


def read_as_of(table: Table, ts: datetime) -> pd.DataFrame:
    ts_ms = int(ts.replace(tzinfo=timezone.utc).timestamp() * 1000)
    candidates = [s for s in table.snapshots() if s.timestamp_ms <= ts_ms]
    if not candidates:
        raise ValueError(f"Tidak ada snapshot pada atau sebelum {ts}")
    snap = max(candidates, key=lambda s: s.timestamp_ms)
    return read_snapshot(table, snap.snapshot_id)


def new_rows_between(table: Table, old_snapshot_id: int, new_snapshot_id: int) -> pd.DataFrame:
    old = read_snapshot(table, old_snapshot_id)
    new = read_snapshot(table, new_snapshot_id)
    return _sorted(new[~new["order_id"].isin(old["order_id"])])
