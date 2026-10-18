"""
ICE02 | Append data ke tabel Iceberg
Tingkat: SEDANG

SOAL
  1. read_orders(db_path, start, end) -> pandas DataFrame
       Ambil order dari data/warehouse.duckdb (tabel orders_clean + order_items_clean) dengan
       order_date di antara start dan end (inklusif, string 'YYYY-MM-DD').
       Kolom (urut): order_id, order_ts (timestamp tengah malam dari order_date),
       distributor_id, amount (jumlah line_amount per order, SEMUA status).
       Urutkan berdasarkan order_id. Buka DuckDB dengan read_only=True.

  2. append_orders(table, df) -> int
       Tambahkan df ke tabel Iceberg, kembalikan snapshot_id BARU.
       Jebakan yang harus Anda tangani:
         - pa.Table.from_pandas menghasilkan kolom nullable dan timestamp nanodetik, sedangkan
           schema tabel punya order_id required dan timestamp mikrodetik. Konversi df ke
           Arrow memakai schema tabel: table.schema().as_arrow().
         - Urutan kolom df bisa berbeda dengan urutan di tabel.
         - Kolom tabel yang tidak ada di df diisi NULL (berguna setelah schema evolution).
       df kosong: jangan membuat snapshot, kembalikan snapshot_id yang sekarang (atau None
       kalau tabel belum punya snapshot).

Uji     : task test-iceberg -- -k ice02
Petunjuk: task hint -- ice02
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from pyiceberg.table import Table


def read_orders(db_path: str | Path, start: str, end: str) -> pd.DataFrame:
    raise NotImplementedError


def append_orders(table: Table, df: pd.DataFrame) -> int | None:
    raise NotImplementedError
