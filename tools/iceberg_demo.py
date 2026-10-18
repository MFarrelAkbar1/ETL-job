"""Playground Iceberg: membuat tabel contoh dari data warehouse, lalu menampilkan isi metadata.

  task iceberg-demo

Hasil di exercises/m6_iceberg/playground/ (boleh dihapus kapan saja, dibuat ulang setiap run).
Tidak memakai jawaban latihan Anda.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import duckdb
import pyarrow as pa
from pyiceberg.partitioning import PartitionField, PartitionSpec
from pyiceberg.schema import Schema
from pyiceberg.transforms import DayTransform
from pyiceberg.types import DoubleType, NestedField, StringType, TimestampType

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "exercises" / "m6_iceberg"))
from ice_base import get_catalog  # noqa: E402

PLAY = ROOT / "exercises" / "m6_iceberg" / "playground"


def read_day(con, day: str):
    return con.execute("""
        SELECT o.order_id, CAST(o.order_date AS TIMESTAMP) AS order_ts, o.distributor_id,
               SUM(i.line_amount) AS amount
        FROM orders_clean o JOIN order_items_clean i USING (order_id)
        WHERE o.order_date = CAST(? AS DATE) GROUP BY ALL ORDER BY 1""", [day]).df()


def main():
    if PLAY.exists():
        shutil.rmtree(PLAY)
    cat = get_catalog(PLAY)
    cat.create_namespace("sales")
    schema = Schema(
        NestedField(1, "order_id", StringType(), required=True),
        NestedField(2, "order_ts", TimestampType(), required=False),
        NestedField(3, "distributor_id", StringType(), required=False),
        NestedField(4, "amount", DoubleType(), required=False),
    )
    spec = PartitionSpec(PartitionField(2, 1000, DayTransform(), "order_day"))
    t = cat.create_table("sales.orders", schema=schema, partition_spec=spec)

    con = duckdb.connect(str(ROOT / "data" / "warehouse.duckdb"), read_only=True)
    for day in ["2025-01-01", "2025-01-02", "2025-01-03"]:
        df = read_day(con, day)
        data = pa.Table.from_pandas(df, schema=t.schema().as_arrow(), preserve_index=False)
        t.append(data)
        print(f"append {day}: {data.num_rows} baris -> snapshot {t.current_snapshot().snapshot_id}")
    con.close()

    with t.update_schema() as u:
        u.add_column("channel", StringType())
    print("schema evolution: tambah kolom 'channel' (field id 5)")

    first = t.snapshots()[0].snapshot_id
    print(f"\nBaris sekarang : {t.scan().to_arrow().num_rows}")
    print(f"Time travel ke snapshot pertama ({first}): {t.scan(snapshot_id=first).to_arrow().num_rows} baris")
    flt = "order_ts >= '2025-01-02T00:00:00' AND order_ts < '2025-01-03T00:00:00'"
    print(f"File dibaca untuk filter 2 Januari: {len(list(t.scan(row_filter=flt).plan_files()))} "
          f"dari {len(list(t.scan().plan_files()))}")

    tdir = PLAY / "warehouse" / "sales" / "orders"
    print(f"\nIsi folder tabel ({tdir}):")
    for p in sorted(tdir.rglob("*")):
        if p.is_file():
            print("  " + p.relative_to(tdir).as_posix())

    md = json.loads(Path(t.metadata_location).read_text(encoding="utf-8"))
    print("\nRingkasan metadata.json terkini:")
    print(f"  format-version    : {md['format-version']}")
    print(f"  schemas           : {len(md['schemas'])} versi, current-schema-id {md['current-schema-id']}")
    print(f"  snapshots         : {len(md['snapshots'])}")
    print(f"  metadata-log      : {len(md['metadata-log'])} versi metadata sebelumnya")
    print(f"  partition-specs   : {md['partition-specs']}")


if __name__ == "__main__":
    main()
