import pandas as pd

from dq_helpers import check_result
from py_check import check

EX, FILE = "dq04", "dq04_referential"

PARENT = pd.DataFrame({"distributor_id": ["D001", "D002", "D003"]})


def _child():
    return pd.DataFrame({"order_id": list("abcdefg"),
                         "distributor_id": ["D001", "D901", "d002", None, "D901", "D003", "D902"]})


def test_orphan(ex):
    r = ex.check_foreign_key(_child(), "distributor_id", PARENT, "distributor_id")
    check_result(r, "relationship:distributor_id->distributor_id", False, 4, 7,
                 "FK (orphan: D901 dua kali, d002, D902; NULL tidak gagal karena allow_null=True)")
    d = r.details
    check(d.get("n_orphan_values") == 3, f"n_orphan_values = {d.get('n_orphan_values')}, seharusnya 3.")
    check(d.get("orphan_values") == ["D901", "D902", "d002"], f"orphan_values = {d.get('orphan_values')}, seharusnya unik dan terurut.")
    check(d.get("null_rows") == 1, f"null_rows = {d.get('null_rows')}, seharusnya 1.")


def test_null_tidak_diizinkan(ex):
    r = ex.check_foreign_key(_child(), "distributor_id", PARENT, "distributor_id", allow_null=False)
    check_result(r, "relationship:distributor_id->distributor_id", False, 5, 7, "allow_null=False")


def test_lulus(ex):
    child = pd.DataFrame({"distributor_id": ["D001", "D003"]})
    check_result(ex.check_foreign_key(child, "distributor_id", PARENT, "distributor_id"),
                 "relationship:distributor_id->distributor_id", True, 0, 2, "semua valid")
