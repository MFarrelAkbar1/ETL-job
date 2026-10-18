"""Membangun tabel Iceberg untuk test tanpa bergantung pada jawaban latihan lain."""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import pyarrow as pa
from pyiceberg.catalog.sql import SqlCatalog
from pyiceberg.partitioning import PartitionField, PartitionSpec
from pyiceberg.schema import Schema
from pyiceberg.transforms import DayTransform
from pyiceberg.types import DoubleType, NestedField, StringType, TimestampType

SCHEMA = Schema(
    NestedField(1, "order_id", StringType(), required=True),
    NestedField(2, "order_ts", TimestampType(), required=False),
    NestedField(3, "distributor_id", StringType(), required=False),
    NestedField(4, "amount", DoubleType(), required=False),
)
SPEC = PartitionSpec(PartitionField(source_id=2, field_id=1000, transform=DayTransform(), name="order_day"))


def catalog(root: Path) -> SqlCatalog:
    root = Path(root).resolve()
    (root / "warehouse").mkdir(parents=True, exist_ok=True)
    return SqlCatalog("test", uri=f"sqlite:///{(root / 'catalog.db').as_posix()}",
                      warehouse=(root / "warehouse").as_posix())


def make_table(root: Path):
    cat = catalog(root)
    cat.create_namespace_if_not_exists("sales")
    return cat.create_table("sales.orders", schema=SCHEMA, partition_spec=SPEC)


def orders_df(ids, day: int = 1, hour: int = 9) -> pd.DataFrame:
    return pd.DataFrame({
        "order_id": list(ids),
        "order_ts": [datetime(2025, 1, day, hour)] * len(ids),
        "distributor_id": ["D001"] * len(ids),
        "amount": [float(i) for i in range(len(ids))],
    })


def append(table, df: pd.DataFrame, pause: float = 0.02):
    schema = table.schema().as_arrow()
    df = df.copy()
    for f in schema:
        if f.name not in df.columns:
            df[f.name] = None
    table.append(pa.Table.from_pandas(df[[f.name for f in schema]], schema=schema, preserve_index=False))
    time.sleep(pause)  # pastikan timestamp_ms snapshot berbeda
    return table.current_snapshot().snapshot_id
