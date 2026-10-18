from pyiceberg.types import DoubleType, StringType, TimestampType

from ice_helpers import catalog
from py_check import check

EX, FILE = "ice01", "ice01_create_table"


def test_schema_dan_partisi(ex, tmp_path):
    cat = catalog(tmp_path)
    t = ex.create_sales_table(cat)
    check(("sales",) in cat.list_namespaces(), "Namespace 'sales' belum dibuat.")
    fields = {f.field_id: f for f in t.schema().fields}
    exp = {1: ("order_id", StringType(), True), 2: ("order_ts", TimestampType(), False),
           3: ("distributor_id", StringType(), False), 4: ("amount", DoubleType(), False)}
    for fid, (name, typ, req) in exp.items():
        f = fields.get(fid)
        check(f is not None, f"Tidak ada field dengan id {fid}. Field id menentukan identitas kolom di Iceberg.")
        check(f.name == name, f"Field id {fid} bernama {f.name!r}, seharusnya {name!r}.")
        check(f.field_type == typ, f"Tipe {name} adalah {f.field_type}, seharusnya {typ}.")
        check(f.required == req, f"{name}: required={f.required}, seharusnya {req}.")
    check(len(fields) == 4, f"Schema harus punya 4 kolom, punya {len(fields)}.")
    pf = t.spec().fields
    check(len(pf) == 1, f"Partition spec harus punya 1 field, punya {len(pf)}.")
    check(pf[0].name == "order_day" and str(pf[0].transform) == "day" and pf[0].source_id == 2,
          f"Partisi harus day(order_ts) bernama 'order_day', didapat {pf[0].name} = {pf[0].transform}(source {pf[0].source_id}).")


def test_idempotent(ex, tmp_path):
    cat = catalog(tmp_path)
    t1 = ex.create_sales_table(cat)
    t2 = ex.create_sales_table(cat)
    check(t2 is not None and t1.metadata_location == t2.metadata_location,
          "Panggilan kedua harus mengembalikan tabel yang sama tanpa membuat ulang.")
    check(cat.list_tables("sales") == [("sales", "orders")], f"Isi namespace: {cat.list_tables('sales')}.")
