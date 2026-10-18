import pandas as pd

from py_check import check

EX, FILE = "p04", "p04_dedup"


def _df():
    return pd.DataFrame({
        "order_id": ["B", "A", "B", "C", "A", "A"],
        "status": ["PENDING", "PENDING", "COMPLETED", "COMPLETED", "CANCELLED", "COMPLETED"],
        # 'A' punya dua versi dengan waktu sama; yang muncul paling akhir harus menang.
        # '2025-01-10 9:00' vs '2025-01-10 10:00': kalau dibandingkan sebagai teks, urutannya salah.
        "updated_at": ["2025-01-10 9:00", "2025-01-01 08:00", "2025-01-10 10:00", "2025-01-05 00:00",
                       "2025-01-03 12:00", "2025-01-03 12:00"],
    })


def test_ambil_terbaru(ex):
    df = _df()
    out = ex.dedup_latest(df)
    check(list(out["order_id"]) == ["A", "B", "C"],
          f"Harus satu baris per order_id, urut order_id. Didapat {list(out['order_id'])}.")
    st = dict(zip(out["order_id"], out["status"]))
    check(st["B"] == "COMPLETED",
          "Untuk order B, versi terbaru adalah jam 10:00. Apakah updated_at dibandingkan sebagai teks? "
          "'9:00' > '10:00' secara alfabet.")
    check(st["A"] == "COMPLETED", "Untuk order A ada dua versi dengan updated_at sama; yang muncul paling akhir yang dipakai.")


def test_bentuk_output(ex):
    df = _df()
    before = df.copy()
    out = ex.dedup_latest(df)
    check(list(out.columns) == list(df.columns), f"Kolom output harus sama: {list(df.columns)}, didapat {list(out.columns)}.")
    check(out["updated_at"].dtype == df["updated_at"].dtype, "Tipe kolom updated_at tidak boleh berubah.")
    check(list(out.index) == [0, 1, 2], "Index harus di-reset.")
    check(df.equals(before), "DataFrame input ikut berubah.")


def test_report(ex):
    r = ex.duplicate_report(_df(), "order_id")
    exp = {"n_rows": 6, "n_unique_keys": 3, "n_duplicate_rows": 3, "n_keys_with_dups": 2}
    for k, v in exp.items():
        check(r.get(k) == v, f"duplicate_report['{k}'] = {r.get(k)}, seharusnya {v}.")
