import pandas as pd

from dq_helpers import check_result
from py_check import check

EX, FILE = "dq02", "dq02_uniqueness"


def test_satu_kolom(ex):
    df = pd.DataFrame({"order_id": ["A", "B", "A", "C", "A", "D", "D", None]})
    r = ex.check_unique(df, "order_id")
    check_result(r, "unique:order_id", False, 6, 8,
                 "order_id (3 baris A + 2 baris D + 1 baris NULL = 6; semua anggota duplikat dihitung)")
    check(r.details.get("duplicate_keys") == 2, f"duplicate_keys = {r.details.get('duplicate_keys')}, seharusnya 2 (A dan D).")
    check(r.details.get("null_keys") == 1, f"null_keys = {r.details.get('null_keys')}, seharusnya 1.")
    check(r.details.get("sample") == [("A",), ("D",)],
          f"sample = {r.details.get('sample')}, seharusnya list of tuple terurut [('A',), ('D',)].")


def test_composite(ex):
    df = pd.DataFrame({"order_id": ["A", "A", "A", "B"], "line_no": [1, 2, 1, 1]})
    r = ex.check_unique(df, ["order_id", "line_no"])
    check_result(r, "unique:order_id,line_no", False, 2, 4, "composite key")
    check(r.details.get("sample") == [("A", 1)], f"sample = {r.details.get('sample')}, seharusnya [('A', 1)].")


def test_lulus(ex):
    r = ex.check_unique(pd.DataFrame({"k": [1, 2, 3]}), ["k"])
    check_result(r, "unique:k", True, 0, 3, "kolom unik")
