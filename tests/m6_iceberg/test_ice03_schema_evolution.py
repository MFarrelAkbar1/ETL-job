from pyiceberg.types import StringType

from ice_helpers import append, make_table, orders_df
from py_check import check

EX, FILE = "ice03", "ice03_schema_evolution"


def test_tambah_kolom(ex, tmp_path):
    t = make_table(tmp_path)
    s_old = append(t, orders_df(["A", "B"]))
    files_before = {f.file.file_path for f in t.scan().plan_files()}
    t = ex.add_column(t, "channel", StringType(), doc="Kanal penjualan")
    f = next((f for f in t.schema().fields if f.name == "channel"), None)
    check(f is not None, "Kolom 'channel' belum ada di schema terkini.")
    check(f.field_id == 5, f"Field id kolom baru {f.field_id}, seharusnya 5 (id berikutnya, tidak pernah dipakai ulang).")
    check(not f.required, "Kolom baru harus optional. Kolom required tidak bisa ditambahkan ke tabel yang sudah berisi data.")
    files_after = {f.file.file_path for f in t.scan().plan_files()}
    check(files_before == files_after, "Data file berubah. Schema evolution seharusnya hanya mengubah metadata.")
    rows = t.scan().to_arrow().to_pylist()
    check(all(r["channel"] is None for r in rows), "Baris lama harus terbaca dengan channel NULL.")
    old_cols = t.scan(snapshot_id=s_old).to_arrow().column_names
    check("channel" not in old_cols, f"Snapshot lama harus tetap memakai schema lama, kolomnya: {old_cols}.")


def test_idempotent(ex, tmp_path):
    t = make_table(tmp_path)
    ex.add_column(t, "channel", StringType())
    n_schemas = len(t.schemas())
    t = ex.add_column(t, "channel", StringType())
    check(len(t.schemas()) == n_schemas, "Memanggil add_column untuk kolom yang sudah ada tidak boleh membuat versi schema baru.")
