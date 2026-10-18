"""Kunci jawaban ICE01."""

from __future__ import annotations

from pyiceberg.catalog import Catalog
from pyiceberg.partitioning import PartitionField, PartitionSpec
from pyiceberg.schema import Schema
from pyiceberg.table import Table
from pyiceberg.transforms import DayTransform
from pyiceberg.types import DoubleType, NestedField, StringType, TimestampType

SCHEMA = Schema(
    NestedField(1, "order_id", StringType(), required=True),
    NestedField(2, "order_ts", TimestampType(), required=False),
    NestedField(3, "distributor_id", StringType(), required=False),
    NestedField(4, "amount", DoubleType(), required=False),
)
# field_id partisi dimulai dari 1000 menurut konvensi Iceberg
SPEC = PartitionSpec(PartitionField(source_id=2, field_id=1000, transform=DayTransform(), name="order_day"))


def create_sales_table(catalog: Catalog) -> Table:
    catalog.create_namespace_if_not_exists("sales")
    return catalog.create_table_if_not_exists("sales.orders", schema=SCHEMA, partition_spec=SPEC)
