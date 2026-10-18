"""
ICE01 | Membuat tabel Iceberg berpartisi
Tingkat: MUDAH

SOAL
  create_sales_table(catalog) -> Table

  1. Buat namespace "sales" kalau belum ada.
  2. Buat tabel "sales.orders" dengan schema (field id harus persis seperti ini):
       1  order_id        string     required
       2  order_ts        timestamp  optional   (tanpa zona waktu)
       3  distributor_id  string     optional
       4  amount          double     optional
  3. Partisi: day(order_ts), nama field partisi "order_day".
  4. Idempotent: kalau dipanggil lagi dan tabel sudah ada, kembalikan tabel yang ada
     (tidak error, tidak membuat ulang).

  Import yang mungkin berguna:
    from pyiceberg.schema import Schema
    from pyiceberg.types import NestedField, StringType, TimestampType, DoubleType
    from pyiceberg.partitioning import PartitionSpec, PartitionField
    from pyiceberg.transforms import DayTransform

Uji     : task test-iceberg -- -k ice01
Petunjuk: task hint -- ice01
"""

from __future__ import annotations

from pyiceberg.catalog import Catalog
from pyiceberg.table import Table


def create_sales_table(catalog: Catalog) -> Table:
    raise NotImplementedError
