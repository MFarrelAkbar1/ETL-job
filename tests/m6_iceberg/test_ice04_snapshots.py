import pandas as pd

from ice_helpers import append, make_table, orders_df
from py_check import check

EX, FILE = "ice04", "ice04_snapshots"
COLS = ["snapshot_id", "parent_id", "operation", "committed_at", "added_records", "total_records"]


def test_daftar(ex, tmp_path):
    t = make_table(tmp_path)
    s1 = append(t, orders_df(["A", "B", "C"]))
    s2 = append(t, orders_df(["D"], day=2))
    df = ex.list_snapshots(t)
    check(list(df.columns) == COLS, f"Kolom harus {COLS}, didapat {list(df.columns)}.")
    check(list(df["snapshot_id"]) == [s1, s2], "Urutan snapshot harus dari yang paling lama.")
    check(pd.isna(df.loc[0, "parent_id"]) and df.loc[1, "parent_id"] == s1,
          "parent_id snapshot pertama None, snapshot kedua menunjuk snapshot pertama.")
    check(list(df["operation"]) == ["append", "append"], f"operation: {list(df['operation'])}.")
    check(list(df["added_records"]) == [3, 1] and list(df["total_records"]) == [3, 4],
          f"added_records {list(df['added_records'])} / total_records {list(df['total_records'])}, seharusnya [3, 1] / [3, 4].")
    exp_ts = pd.to_datetime(t.snapshots()[0].timestamp_ms, unit="ms")
    check(pd.Timestamp(df.loc[0, "committed_at"]) == exp_ts, f"committed_at {df.loc[0, 'committed_at']}, seharusnya {exp_ts}.")


def test_kosong(ex, tmp_path):
    df = ex.list_snapshots(make_table(tmp_path))
    check(len(df) == 0 and list(df.columns) == COLS, "Tabel tanpa snapshot harus menghasilkan DataFrame kosong berkolom lengkap.")
