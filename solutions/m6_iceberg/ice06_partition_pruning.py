"""Kunci jawaban ICE06."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
from pyiceberg.table import Table


def _filter(start: date, end: date) -> str:
    # batas atas eksklusif di hari berikutnya: aman untuk timestamp dengan jam/menit/detik
    return (f"order_ts >= '{start.isoformat()}T00:00:00' AND "
            f"order_ts < '{(end + timedelta(days=1)).isoformat()}T00:00:00'")


def files_scanned(table: Table, start: date, end: date) -> tuple[int, int]:
    planned = len(list(table.scan(row_filter=_filter(start, end)).plan_files()))
    total = len(list(table.scan().plan_files()))
    return planned, total


def read_range(table: Table, start: date, end: date) -> pd.DataFrame:
    df = table.scan(row_filter=_filter(start, end)).to_pandas()
    return df.sort_values("order_id").reset_index(drop=True)
