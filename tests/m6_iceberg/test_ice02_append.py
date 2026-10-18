from pathlib import Path

import duckdb
import pandas as pd

from ice_helpers import make_table, orders_df
from py_check import check

EX, FILE = "ice02", "ice02_append"
DB = Path(__file__).resolve().parents[2] / "data" / "warehouse.duckdb"


def test_read_orders(ex):
    df = ex.read_orders(DB, "2025-01-01", "2025-01-03")
    check(list(df.columns) == ["order_id", "order_ts", "distributor_id", "amount"], f"Kolom: {list(df.columns)}.")
    con = duckdb.connect(str(DB), read_only=True)
    n, total = con.execute("""SELECT COUNT(DISTINCT o.order_id), SUM(i.line_amount) FROM orders_clean o
        JOIN order_items_clean i USING (order_id) WHERE o.order_date BETWEEN DATE '2025-01-01' AND DATE '2025-01-03'""").fetchone()
    con.close()
    check(len(df) == n, f"Jumlah order {len(df)}, seharusnya {n} (satu baris per order, semua status, inklusif).")
    check(abs(df["amount"].sum() - total) < 0.01, "Total amount tidak sama dengan jumlah line_amount pada rentang itu.")
    check(pd.api.types.is_datetime64_any_dtype(df["order_ts"]), f"order_ts harus timestamp, didapat {df['order_ts'].dtype}.")
    check(df["order_id"].is_monotonic_increasing, "Hasil harus urut order_id.")


def test_append_dan_snapshot(ex, tmp_path):
    t = make_table(tmp_path)
    s1 = ex.append_orders(t, orders_df(["A", "B"]))
    check(s1 is not None and t.current_snapshot() is not None and s1 == t.current_snapshot().snapshot_id,
          "Return value harus snapshot_id terbaru setelah append.")
    df2 = orders_df(["C"], day=2)[["amount", "order_id", "distributor_id", "order_ts"]]  # urutan kolom diacak
    s2 = ex.append_orders(t, df2)
    check(s2 != s1, "Append kedua harus membuat snapshot baru.")
    check(len(t.snapshots()) == 2, f"Tabel seharusnya punya 2 snapshot, punya {len(t.snapshots())}.")
    check(t.scan().to_arrow().num_rows == 3, "Total baris setelah dua append seharusnya 3.")


def test_kolom_tambahan_dan_df_kosong(ex, tmp_path):
    from pyiceberg.types import StringType
    t = make_table(tmp_path)
    with t.update_schema() as u:
        u.add_column("channel", StringType())
    s = ex.append_orders(t, orders_df(["A"]))
    rows = t.scan().to_arrow().to_pylist()
    check(len(rows) == 1 and rows[0]["channel"] is None,
          "Kolom tabel yang tidak ada di df (channel) harus diisi NULL.")
    n_snap = len(t.snapshots())
    s_empty = ex.append_orders(t, orders_df([]))
    check(len(t.snapshots()) == n_snap and s_empty == s, "df kosong tidak boleh membuat snapshot baru.")
