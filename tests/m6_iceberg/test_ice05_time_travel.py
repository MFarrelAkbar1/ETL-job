from datetime import datetime, timedelta, timezone

from ice_helpers import append, make_table, orders_df
from py_check import check, expect_raises

EX, FILE = "ice05", "ice05_time_travel"


def _setup(tmp_path):
    t = make_table(tmp_path)
    ids = [append(t, orders_df(["A", "B"])), append(t, orders_df(["C"], day=2)), append(t, orders_df(["D", "E"], day=3))]
    times = [datetime.fromtimestamp(s.timestamp_ms / 1000, tz=timezone.utc).replace(tzinfo=None) for s in t.snapshots()]
    return t, ids, times


def test_read_snapshot(ex, tmp_path):
    t, ids, _ = _setup(tmp_path)
    df = ex.read_snapshot(t, ids[1])
    check(list(df["order_id"]) == ["A", "B", "C"], f"Isi snapshot ke-2: {list(df['order_id'])}, seharusnya A, B, C.")
    check(list(df.index) == [0, 1, 2], "Index harus di-reset.")


def test_read_as_of(ex, tmp_path):
    t, ids, times = _setup(tmp_path)
    df = ex.read_as_of(t, times[1] + timedelta(milliseconds=5))
    check(list(df["order_id"]) == ["A", "B", "C"], f"Pada waktu commit ke-2 (+5 ms), isi tabel {list(df['order_id'])}.")
    df_exact = ex.read_as_of(t, times[0])
    check(list(df_exact["order_id"]) == ["A", "B"], "Waktu yang PERSIS sama dengan commit harus memakai snapshot itu (pada atau sebelum).")
    expect_raises(ValueError, ex.read_as_of, t, times[0] - timedelta(seconds=5),
                  msg="Waktu sebelum snapshot pertama harus raise ValueError.")


def test_new_rows(ex, tmp_path):
    t, ids, _ = _setup(tmp_path)
    df = ex.new_rows_between(t, ids[0], ids[2])
    check(list(df["order_id"]) == ["C", "D", "E"], f"Baris baru antara snapshot 1 dan 3: {list(df['order_id'])}.")
