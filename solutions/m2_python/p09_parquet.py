"""Kunci jawaban P09."""

from __future__ import annotations

import uuid
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def write_partitioned(df: pd.DataFrame, root: str | Path, partition_cols: list[str],
                      mode: str = "overwrite_partitions") -> list[str]:
    missing = [c for c in partition_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom partisi tidak ada di df: {missing}")
    behavior = {"overwrite_partitions": "delete_matching", "append": "overwrite_or_ignore"}
    if mode not in behavior:
        raise ValueError(f"mode tidak dikenal: {mode}")

    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_to_dataset(
        table, root_path=str(root), partition_cols=partition_cols,
        existing_data_behavior=behavior[mode],
        # nama file unik supaya mode append tidak menimpa file lama
        basename_template=f"part-{uuid.uuid4().hex}-{{i}}.parquet",
    )
    parts = df[partition_cols].drop_duplicates()
    return sorted("/".join(f"{c}={row[c]}" for c in partition_cols) for _, row in parts.iterrows())
