"""
P09 | Load: menulis Parquet terpartisi secara idempotent
Tingkat: SEDANG

SOAL
  write_partitioned(df, root, partition_cols, mode="overwrite_partitions") -> list[str]

  Tulis df ke folder root sebagai dataset Parquet terpartisi gaya Hive
  (root/year=2025/month=3/xxx.parquet). Gunakan pyarrow.

  mode:
    "overwrite_partitions"  partisi yang ADA di df ditimpa seluruhnya, partisi lain di root
                            tidak disentuh (dynamic partition overwrite). Menjalankan fungsi
                            dua kali dengan df yang sama tidak boleh menggandakan data.
    "append"                tambahkan file baru tanpa menghapus apa pun. File lama tidak boleh
                            tertimpa walaupun namanya mirip.
    lainnya                 raise ValueError

  Kalau ada partition_cols yang tidak ada di df, raise ValueError.

  Return: daftar partisi yang ditulis, unik dan terurut, dengan pemisah '/', contoh
  ['year=2025/month=1', 'year=2025/month=2'].

Uji     : task test-python -- -k p09
Petunjuk: task hint -- p09
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_partitioned(df: pd.DataFrame, root: str | Path, partition_cols: list[str],
                      mode: str = "overwrite_partitions") -> list[str]:
    raise NotImplementedError
