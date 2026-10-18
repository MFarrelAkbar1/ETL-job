import numpy as np
import pandas as pd

from py_check import check

EX, FILE = "p02", "p02_clean_strings"


def test_normalize_product_code(ex):
    s = pd.Series(["prd-0044 ", " PRD-0063 ", "Prd - 0001", "PRD-0002", "   ", np.nan],
                  index=[10, 11, 12, 13, 14, 15])
    out = ex.normalize_product_code(s)
    check(isinstance(out, pd.Series), "Fungsi harus mengembalikan pandas Series.")
    check(list(out.index) == list(s.index), "Index output harus sama dengan input.")
    exp = ["PRD-0044", "PRD-0063", "PRD-0001", "PRD-0002"]
    check(list(out.iloc[:4]) == exp, f"Hasil normalisasi 4 nilai pertama: {list(out.iloc[:4])}, seharusnya {exp}.")
    check(pd.isna(out.iloc[4]), "String yang hanya berisi spasi harus menjadi NaN, bukan string kosong.")
    check(pd.isna(out.iloc[5]), "NaN harus tetap NaN (hati-hati: astype(str) mengubah NaN menjadi 'nan').")


def test_normalize_tidak_ubah_input(ex):
    s = pd.Series([" prd-1 "])
    ex.normalize_product_code(s)
    check(s.iloc[0] == " prd-1 ", "Series input ikut berubah. Kembalikan Series baru.")


def test_standardize_status(ex):
    s = pd.Series(["completed", " Complete", "DONE", "Cancelled", "canceled ", "CANCEL",
                   "pending", "Waiting", "refund", np.nan, ""])
    out = list(ex.standardize_status(s))
    exp = ["COMPLETED"] * 3 + ["CANCELLED"] * 3 + ["PENDING"] * 2 + ["UNKNOWN"] * 3
    bad = [(v, o, e) for v, o, e in zip(s.tolist(), out, exp) if o != e]
    check(not bad, "Beberapa status salah dipetakan (input, hasil Anda, seharusnya):\n  "
          + "\n  ".join(map(str, bad[:5])))
