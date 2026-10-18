"""
ICE03 | Schema evolution
Tingkat: MUDAH

SOAL
  add_column(table, name, iceberg_type, doc=None) -> Table

  Tambahkan kolom OPTIONAL baru ke tabel tanpa menulis ulang data. Idempotent: kalau kolom
  sudah ada, jangan error dan jangan menambah apa pun. Kembalikan tabel (sudah ter-update).

  Setelah lulus, perhatikan di test:
  - field id kolom baru adalah id berikutnya (5), bukan posisi kolom
  - data lama terbaca dengan nilai NULL untuk kolom baru
  - snapshot lama tetap memakai schema lama (time travel melihat kolom yang lama)

  Import yang mungkin berguna: table.update_schema() sebagai context manager.

Uji     : task test-iceberg -- -k ice03
Petunjuk: task hint -- ice03
"""

from __future__ import annotations

from pyiceberg.table import Table
from pyiceberg.types import IcebergType


def add_column(table: Table, name: str, iceberg_type: IcebergType, doc: str | None = None) -> Table:
    raise NotImplementedError
