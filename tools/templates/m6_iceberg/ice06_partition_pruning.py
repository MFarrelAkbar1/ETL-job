"""
ICE06 | Hidden partitioning dan pruning
Tingkat: SEDANG

SOAL
  Tabel dipartisi day(order_ts). Anda TIDAK memfilter kolom partisi (order_day), cukup
  memfilter kolom asli order_ts, dan Iceberg yang menerjemahkannya.

  1. files_scanned(table, start, end) -> (int, int)
       start dan end adalah date (inklusif). Kembalikan (jumlah data file yang direncanakan
       dibaca dengan filter order_ts di rentang itu, jumlah seluruh data file tabel).
       Gunakan table.scan(row_filter=...).plan_files().

  2. read_range(table, start, end) -> DataFrame
       Baris dengan order_ts di antara start 00:00 sampai end 23:59:59.999999 (inklusif per
       hari), urut order_id, index di-reset.

  Petunjuk sintaks filter string PyIceberg:
      "order_ts >= '2025-01-02T00:00:00' AND order_ts < '2025-01-04T00:00:00'"

Uji     : task test-iceberg -- -k ice06
Petunjuk: task hint -- ice06
"""

from __future__ import annotations

from datetime import date

import pandas as pd
from pyiceberg.table import Table


def files_scanned(table: Table, start: date, end: date) -> tuple[int, int]:
    raise NotImplementedError


def read_range(table: Table, start: date, end: date) -> pd.DataFrame:
    raise NotImplementedError
