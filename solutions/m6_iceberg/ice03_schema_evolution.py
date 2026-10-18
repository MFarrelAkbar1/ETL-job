"""Kunci jawaban ICE03."""

from __future__ import annotations

from pyiceberg.table import Table
from pyiceberg.types import IcebergType


def add_column(table: Table, name: str, iceberg_type: IcebergType, doc: str | None = None) -> Table:
    if name in [f.name for f in table.schema().fields]:
        return table
    # perubahan schema hanya menulis metadata.json baru; data file tidak disentuh
    with table.update_schema() as update:
        update.add_column(name, iceberg_type, doc=doc)
    return table
