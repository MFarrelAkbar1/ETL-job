"""
ICE05 | Time travel
Tingkat: SEDANG

SOAL
  1. read_snapshot(table, snapshot_id) -> DataFrame
       Isi tabel PADA snapshot tersebut, diurutkan berdasarkan order_id, index di-reset.
       Kolom mengikuti schema yang berlaku pada snapshot itu.

  2. read_as_of(table, ts) -> DataFrame
       Isi tabel pada waktu ts (datetime UTC tanpa zona): pakai snapshot TERAKHIR yang
       di-commit pada atau sebelum ts. Kalau ts lebih awal dari snapshot pertama,
       raise ValueError. Urut order_id, index di-reset.

  3. new_rows_between(table, old_snapshot_id, new_snapshot_id) -> DataFrame
       Baris (berdasarkan order_id) yang ada di snapshot baru tetapi tidak ada di snapshot lama.
       Kolom mengikuti snapshot baru, urut order_id, index di-reset.

Uji     : task test-iceberg -- -k ice05
Petunjuk: task hint -- ice05
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd
from pyiceberg.table import Table


def read_snapshot(table: Table, snapshot_id: int) -> pd.DataFrame:
    raise NotImplementedError


def read_as_of(table: Table, ts: datetime) -> pd.DataFrame:
    raise NotImplementedError


def new_rows_between(table: Table, old_snapshot_id: int, new_snapshot_id: int) -> pd.DataFrame:
    raise NotImplementedError
