import duckdb
import pandas as pd

from py_check import check, expect_raises

EX, FILE = "p11", "p11_load"


def _df(ids, val):
    return pd.DataFrame({"id": ids, "name": [f"n{i}" for i in ids], "val": [val] * len(ids)})


def _read(db, t="t"):
    con = duckdb.connect(str(db), read_only=True)
    try:
        return con.execute(f"SELECT * FROM {t} ORDER BY id").df()
    finally:
        con.close()


def test_append_replace(ex, tmp_path):
    db = tmp_path / "w.duckdb"
    n = ex.load_to_duckdb(_df([1, 2], 1.0), db, "t")
    check(n == 2, f"Setelah append pertama harus 2 baris, return {n}.")
    n = ex.load_to_duckdb(_df([3], 1.0), db, "t", mode="append")
    check(n == 3, f"Append kedua harus 3 baris, return {n}.")
    n = ex.load_to_duckdb(_df([7], 9.0), db, "t", mode="replace")
    check(n == 1 and list(_read(db)["id"]) == [7], "Mode replace harus mengganti seluruh isi tabel.")


def test_upsert_idempotent(ex, tmp_path):
    db = tmp_path / "w.duckdb"
    ex.load_to_duckdb(_df([1, 2, 3], 1.0), db, "t")
    batch = _df([2, 3, 4], 2.0)
    ex.load_to_duckdb(batch, db, "t", mode="upsert", key="id")
    n = ex.load_to_duckdb(batch, db, "t", mode="upsert", key="id")
    out = _read(db)
    check(n == 4, f"Setelah upsert (dua kali) tabel harus 4 baris, didapat {n}. Upsert harus idempotent.")
    check(list(out["val"]) == [1.0, 2.0, 2.0, 2.0], f"Nilai val setelah upsert {list(out['val'])}, seharusnya [1, 2, 2, 2].")


def test_upsert_validasi(ex, tmp_path):
    db = tmp_path / "w.duckdb"
    ex.load_to_duckdb(_df([1], 1.0), db, "t")
    expect_raises(ValueError, ex.load_to_duckdb, _df([1], 1.0), db, "t", mode="upsert",
                  msg="Upsert tanpa key harus raise ValueError.")
    expect_raises(ValueError, ex.load_to_duckdb, _df([5, 5], 1.0), db, "t", mode="upsert", key="id",
                  msg="Batch dengan key duplikat harus raise ValueError.")
    check(list(_read(db)["id"]) == [1], "Tabel tidak boleh berubah kalau validasi gagal.")
    expect_raises(ValueError, ex.load_to_duckdb, _df([1], 1.0), db, "t", mode="merge",
                  msg="mode tidak dikenal harus raise ValueError.")


def test_atomik(ex, tmp_path):
    db = tmp_path / "w.duckdb"
    ex.load_to_duckdb(_df([1, 2], 1.0), db, "t")
    bad = pd.DataFrame({"id": [9], "name": ["x"], "val": ["bukan angka"]})
    try:
        ex.load_to_duckdb(bad, db, "t", mode="replace")
    except Exception:  # noqa: BLE001
        pass
    out = _read(db)
    check(list(out["id"]) == [1, 2], "Load yang gagal di tengah membuat isi tabel berubah. Gunakan transaksi.")
