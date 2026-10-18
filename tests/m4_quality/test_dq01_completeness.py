import numpy as np
import pandas as pd

from dq_helpers import check_result
from py_check import check, expect_raises

EX, FILE = "dq01", "dq01_completeness"


def _df():
    return pd.DataFrame({
        "order_id": ["A", "B", "C", "D", "E"],
        "city": ["Bandung", None, "  ", "", "N/A"],
        "price": [1.0, np.nan, 0.0, 2.0, 3.0],
        "ts": pd.to_datetime(["2025-01-01", None, "2025-01-02", "2025-01-03", "2025-01-04"]),
    })


def test_hitung_kosong(ex):
    res = ex.check_completeness(_df(), ["order_id", "city", "price", "ts"])
    check(isinstance(res, list) and len(res) == 4, "Harus mengembalikan list berisi satu CheckResult per kolom.")
    check_result(res[0], "not_null:order_id", True, 0, 5, "order_id")
    check_result(res[1], "not_null:city", False, 3, 5,
                 "city (None, string kosong, dan string berisi spasi dihitung kosong; 'N/A' tidak)")
    check_result(res[2], "not_null:price", False, 1, 5, "price (0.0 bukan kosong)")
    check_result(res[3], "not_null:ts", False, 1, 5, "ts (NaT dihitung kosong)")
    check(res[1].details.get("null_rate") == 0.6, f"details['null_rate'] untuk city = {res[1].details.get('null_rate')}, seharusnya 0.6.")


def test_threshold(ex):
    res = ex.check_completeness(_df(), ["price", "city"], max_null_rate=0.2)
    check(res[0].passed is True or res[0].passed == True, "price punya null_rate 0.2 dan batasnya 0.2, seharusnya lulus (<=).")
    check(not res[1].passed, "city punya null_rate 0.6, seharusnya gagal dengan batas 0.2.")


def test_df_kosong_dan_kolom_salah(ex):
    res = ex.check_completeness(pd.DataFrame({"a": []}), ["a"])
    check(res[0].passed and res[0].total_rows == 0, "DataFrame kosong dianggap lulus dengan total_rows 0.")
    e = expect_raises(KeyError, ex.check_completeness, _df(), ["tidak_ada"],
                      msg="Kolom yang tidak ada harus raise KeyError.")
    check("tidak_ada" in str(e), "Pesan KeyError harus menyebut nama kolom.")
