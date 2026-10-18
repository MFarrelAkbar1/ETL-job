import pandas as pd

from dq_helpers import check_result
from py_check import check

EX, FILE = "dq06", "dq06_reconciliation"


def _data():
    src = pd.DataFrame({"order_id": ["O1", "O2", "O3", "O4", "O5"], "amount": [100.0, 200.0, 300.0, 400.0, 50.0]})
    tgt = pd.DataFrame({"order_id": ["O1", "O2", "O2", "O3", "O5", "O9"],
                        "amount": [100.0, 100.0, 100.0, 300.5, 50.004, 70.0]})
    return src, tgt


def test_status(ex):
    src, tgt = _data()
    out = ex.reconcile(src, tgt, "order_id", "amount")
    check(isinstance(out, tuple) and len(out) == 2, "reconcile harus mengembalikan tuple (CheckResult, DataFrame).")
    r, diff = out
    check(list(diff.columns) == ["order_id", "status", "source_amount", "target_amount"],
          f"Kolom DataFrame selisih: {list(diff.columns)}.")
    got = dict(zip(diff["order_id"], diff["status"]))
    exp = {"O3": "AMOUNT_DIFF", "O4": "ONLY_SOURCE", "O9": "ONLY_TARGET"}
    check(got == exp, f"Status per key {got}, seharusnya {exp}.\n"
          "  O2: target punya 2 baris (100 + 100 = 200), cocok kalau diagregasi dulu.\n"
          "  O5: selisih 0.004 masih dalam toleransi 0.01.")
    check(list(diff["order_id"]) == ["O3", "O4", "O9"] and list(diff.index) == [0, 1, 2], "Urutkan berdasarkan key dan reset index.")
    check(pd.isna(diff.loc[1, "target_amount"]) and pd.isna(diff.loc[2, "source_amount"]), "Sisi yang tidak ada harus NaN.")


def test_check_result(ex):
    src, tgt = _data()
    r, _ = ex.reconcile(src, tgt, "order_id", "amount")
    check_result(r, "reconcile:order_id", False, 3, 6, "rekonsiliasi (6 key unik gabungan)")
    d = r.details
    exp = {"only_source": 1, "only_target": 1, "amount_diff": 1, "source_total": 1050.0, "target_total": 720.5}
    bad = {k: (d.get(k), v) for k, v in exp.items() if d.get(k) != v}
    check(not bad, f"details salah (hasil Anda, seharusnya): {bad}")


def test_cocok(ex):
    df = pd.DataFrame({"k": [1, 2], "v": [1.0, 2.0]})
    r, diff = ex.reconcile(df, df.copy(), "k", "v")
    check_result(r, "reconcile:k", True, 0, 2, "kedua sisi sama")
    check(len(diff) == 0, "DataFrame selisih harus kosong kalau semua cocok.")
