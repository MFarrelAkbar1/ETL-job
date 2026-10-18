import numpy as np
import pandas as pd

from dq_helpers import check_result
from py_check import check

EX, FILE = "dq03", "dq03_validity"


def test_range(ex):
    df = pd.DataFrame({"price": ["1000", "-500", "0", "abc", None, "2500.5", "999999"]})
    r = ex.check_range(df, "price", min_value=0.01, max_value=100000)
    check_result(r, "range:price", False, 4, 6,
                 "range (gagal: -500, 0, 'abc', 999999; NULL diabaikan dan tidak ikut total)")
    check(r.details.get("min_found") == -500.0 and r.details.get("max_found") == 999999.0,
          f"min_found/max_found = {r.details.get('min_found')}/{r.details.get('max_found')}, seharusnya -500.0/999999.0.")


def test_range_inclusive(ex):
    df = pd.DataFrame({"q": [1, 5, 10]})
    check_result(ex.check_range(df, "q", 1, 10), "range:q", True, 0, 3, "inclusive=True")
    check_result(ex.check_range(df, "q", 1, 10, inclusive=False), "range:q", False, 2, 3, "inclusive=False")
    check_result(ex.check_range(df, "q", max_value=4), "range:q", False, 2, 3, "hanya max_value")


def test_allowed_values(ex):
    df = pd.DataFrame({"status": ["COMPLETED", "completed", " COMPLETED", "PENDING", np.nan, "REFUND"]})
    r = ex.check_allowed_values(df, "status", ["COMPLETED", "PENDING", "CANCELLED"])
    check_result(r, "accepted_values:status", False, 3, 5, "case sensitive")
    check(r.details.get("unexpected") == [" COMPLETED", "REFUND", "completed"],
          f"details['unexpected'] = {r.details.get('unexpected')}, seharusnya nilai asli unik terurut.")
    r2 = ex.check_allowed_values(df, "status", ["COMPLETED", "PENDING"], case_sensitive=False)
    check_result(r2, "accepted_values:status", False, 2, 5,
                 "case_sensitive=False (' COMPLETED' tetap gagal karena spasi tidak diabaikan)")


def test_regex(ex):
    df = pd.DataFrame({"code": ["PRD-0001", "prd-0002", "PRD-0003 ", "XPRD-0004", "PRD-12", None, "PRD-0001"]})
    r = ex.check_regex(df, "code", r"PRD-\d{4}")
    check_result(r, "regex:code", False, 4, 6, "regex harus full match")
    check(r.details.get("sample") == ["PRD-0003 ", "PRD-12", "XPRD-0004", "prd-0002"],
          f"details['sample'] = {r.details.get('sample')}. 'XPRD-0004' gagal karena harus cocok PENUH.")
