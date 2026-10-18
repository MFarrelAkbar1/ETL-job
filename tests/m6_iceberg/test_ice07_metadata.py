from pyiceberg.types import StringType

from ice_helpers import append, make_table, orders_df
from py_check import check

EX, FILE = "ice07", "ice07_metadata"


def test_summary(ex, tmp_path):
    t = make_table(tmp_path)
    append(t, orders_df(["A"]))
    with t.update_schema() as u:
        u.add_column("channel", StringType())
    append(t, orders_df(["B"], day=2))
    m = t.metadata
    exp = {
        "format_version": m.format_version,
        "current_snapshot_id": m.current_snapshot_id,
        "n_snapshots": len(m.snapshots),
        "n_schemas": len(m.schemas),
        "current_schema_id": m.current_schema_id,
        "n_previous_metadata": len(m.metadata_log),
        "partition_fields": [("order_day", "day", "order_ts")],
        "manifest_list_exists": True,
    }
    got = ex.metadata_summary(t)
    bad = {k: (got.get(k), v) for k, v in exp.items() if (list(map(tuple, got.get(k))) if k == "partition_fields" and got.get(k) is not None else got.get(k)) != v}
    check(not bad, "Nilai yang belum tepat (hasil Anda, seharusnya):\n  " + "\n  ".join(f"{k}: {a!r} vs {b!r}" for k, (a, b) in bad.items()))


def test_tabel_kosong(ex, tmp_path):
    got = ex.metadata_summary(make_table(tmp_path))
    check(got.get("current_snapshot_id") is None, "Tabel tanpa snapshot: current_snapshot_id harus None.")
    check(got.get("n_snapshots") == 0 and got.get("manifest_list_exists") is False,
          "Tabel tanpa snapshot: n_snapshots 0 dan manifest_list_exists False.")
