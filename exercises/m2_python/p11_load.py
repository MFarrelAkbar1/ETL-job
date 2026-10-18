"""
P11 | Load: memuat DataFrame ke DuckDB (append, replace, upsert)
Tingkat: SEDANG

SOAL
  load_to_duckdb(df, db_path, table, mode="append", key=None) -> int

  Return: jumlah baris di tabel SETELAH load.
  Kalau tabel belum ada, buat dari skema df.

  mode:
    "append"   tambahkan semua baris
    "replace"  ganti seluruh isi tabel dengan df
    "upsert"   baris dengan key yang sudah ada diganti, key baru ditambahkan.
               key wajib (string atau list kolom), kalau tidak ada raise ValueError.
               Kalau df punya key duplikat, raise ValueError SEBELUM menyentuh tabel.
               Upsert harus idempotent: dijalankan dua kali hasilnya sama.
    lainnya    raise ValueError

  Operasi harus atomik: kalau gagal di tengah, tabel tidak boleh setengah terisi
  (gunakan transaksi). Tutup koneksi setelah selesai.

Uji     : task test-python -- -k p11
Petunjuk: task hint -- p11
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd


def load_to_duckdb(df: pd.DataFrame, db_path: str | Path, table: str, mode: str = "append",
                   key: str | list[str] | None = None) -> int:
    raise NotImplementedError
