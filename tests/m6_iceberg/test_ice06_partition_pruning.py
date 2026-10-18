from datetime import date

from ice_helpers import append, make_table, orders_df
from py_check import check

EX, FILE = "ice06", "ice06_partition_pruning"


def _setup(tmp_path):
    t = make_table(tmp_path)
    for day in range(1, 6):  # 5 hari, satu file per hari
        append(t, orders_df([f"O{day}a", f"O{day}b"], day=day, hour=23), pause=0)
    return t


def test_pruning(ex, tmp_path):
    t = _setup(tmp_path)
    got = ex.files_scanned(t, date(2025, 1, 2), date(2025, 1, 3))
    check(tuple(got) == (2, 5), f"files_scanned = {got}, seharusnya (2, 5): hanya file partisi 2 dan 3 Januari yang dibaca.")
    one = ex.files_scanned(t, date(2025, 1, 5), date(2025, 1, 5))
    check(tuple(one) == (1, 5), f"Satu hari seharusnya (1, 5), didapat {one}.")


def test_read_range(ex, tmp_path):
    t = _setup(tmp_path)
    df = ex.read_range(t, date(2025, 1, 2), date(2025, 1, 3))
    check(list(df["order_id"]) == ["O2a", "O2b", "O3a", "O3b"],
          f"Hasil {list(df['order_id'])}. Order jam 23:00 di tanggal akhir harus ikut (rentang inklusif per hari).")
