import pandas as pd

from py_check import check

EX, FILE = "p05", "p05_validate"


def _items():
    return pd.DataFrame({
        "order_item_id": ["1", "2", "3", "4", "5", "6", "7", "8"],
        "quantity":      ["2", "3", None, "0", "abc", "5", None, "4"],
        "unit_price":    ["1000", "-500", "2000", "1500", "100", None, "0", "2500.5"],
    })


def test_pembagian(ex):
    valid, rejected = ex.split_valid_invalid(_items())
    check(len(valid) + len(rejected) == 8, f"Ada baris yang hilang: {len(valid)} valid + {len(rejected)} ditolak, input 8.")
    check(list(valid["order_item_id"]) == ["1", "8"], f"Baris valid seharusnya item 1 dan 8, didapat {list(valid['order_item_id'])}.")
    check("reject_reason" not in valid.columns, "valid tidak boleh punya kolom reject_reason.")


def test_alasan_berurutan(ex):
    _, rejected = ex.split_valid_invalid(_items())
    check("reject_reason" in rejected.columns, "rejected harus punya kolom reject_reason.")
    got = dict(zip(rejected["order_item_id"], rejected["reject_reason"]))
    exp = {"2": "unit_price_non_positive", "3": "quantity_null", "4": "quantity_non_positive",
           "5": "quantity_null", "6": "unit_price_null", "7": "unit_price_non_positive"}
    bad = {k: (got.get(k), v) for k, v in exp.items() if got.get(k) != v}
    check(not bad, "reject_reason salah untuk item (hasil Anda, seharusnya): "
          f"{bad}. Ingat aturan diperiksa berurutan; item 7 punya dua masalah.")


def test_tipe_valid(ex):
    valid, rejected = ex.split_valid_invalid(_items())
    check(str(valid["quantity"].dtype) == "int64", f"quantity di valid harus int64, didapat {valid['quantity'].dtype}.")
    check(str(valid["unit_price"].dtype) == "float64", f"unit_price di valid harus float64, didapat {valid['unit_price'].dtype}.")
    check(list(valid.index) == list(range(len(valid))) and list(rejected.index) == list(range(len(rejected))),
          "Index valid dan rejected harus di-reset.")
