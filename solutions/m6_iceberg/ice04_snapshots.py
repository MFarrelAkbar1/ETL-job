"""Kunci jawaban ICE04."""

from __future__ import annotations

import pandas as pd
from pyiceberg.table import Table

COLUMNS = ["snapshot_id", "parent_id", "operation", "committed_at", "added_records", "total_records"]


def list_snapshots(table: Table) -> pd.DataFrame:
    rows = []
    for s in table.snapshots():
        summary = s.summary
        rows.append({
            "snapshot_id": s.snapshot_id,
            "parent_id": s.parent_snapshot_id,
            "operation": summary.operation.value if summary else None,
            "committed_at": pd.to_datetime(s.timestamp_ms, unit="ms"),
            "added_records": int(summary.get("added-records", 0)) if summary else 0,
            "total_records": int(summary.get("total-records", 0)) if summary else 0,
        })
    df = pd.DataFrame(rows, columns=COLUMNS)
    return df.sort_values("committed_at", kind="stable").reset_index(drop=True)
