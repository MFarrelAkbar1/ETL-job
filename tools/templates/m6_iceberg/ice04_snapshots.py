"""
ICE04 | Melihat snapshot
Tingkat: MUDAH

SOAL
  list_snapshots(table) -> pandas DataFrame

  Satu baris per snapshot, urut dari yang paling lama. Kolom (urut):
    snapshot_id    int
    parent_id      int atau None (snapshot pertama tidak punya parent)
    operation      string, contoh 'append', 'overwrite'
    committed_at   pandas Timestamp (dari timestamp_ms snapshot, UTC tanpa zona)
    added_records  int   (dari summary 'added-records', 0 kalau tidak ada)
    total_records  int   (dari summary 'total-records', 0 kalau tidak ada)
  Tabel tanpa snapshot menghasilkan DataFrame kosong dengan kolom di atas.

Uji     : task test-iceberg -- -k ice04
Petunjuk: task hint -- ice04
"""

from __future__ import annotations

import pandas as pd
from pyiceberg.table import Table

COLUMNS = ["snapshot_id", "parent_id", "operation", "committed_at", "added_records", "total_records"]


def list_snapshots(table: Table) -> pd.DataFrame:
    raise NotImplementedError
