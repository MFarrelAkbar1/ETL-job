"""Kunci jawaban ICE02."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd
import pyarrow as pa
from pyiceberg.table import Table


def read_orders(db_path: str | Path, start: str, end: str) -> pd.DataFrame:
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        return con.execute("""
            SELECT o.order_id, CAST(o.order_date AS TIMESTAMP) AS order_ts, o.distributor_id,
                   SUM(i.line_amount) AS amount
            FROM orders_clean o JOIN order_items_clean i ON i.order_id = o.order_id
            WHERE o.order_date BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
            GROUP BY ALL ORDER BY o.order_id
        """, [start, end]).df()
    finally:
        con.close()


def append_orders(table: Table, df: pd.DataFrame) -> int | None:
    current = table.current_snapshot()
    if df.empty:
        return current.snapshot_id if current else None
    arrow_schema = table.schema().as_arrow()
    df = df.copy()
    for field in arrow_schema:
        if field.name not in df.columns:
            df[field.name] = None  # kolom baru hasil schema evolution
    # from_pandas dengan schema tabel: urutan kolom, nullability, dan presisi timestamp ikut tabel
    arrow = pa.Table.from_pandas(df[[f.name for f in arrow_schema]], schema=arrow_schema, preserve_index=False)
    table.append(arrow)
    return table.current_snapshot().snapshot_id
