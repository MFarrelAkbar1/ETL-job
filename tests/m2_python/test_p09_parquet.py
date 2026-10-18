import pandas as pd

from py_check import check, expect_raises

EX, FILE = "p09", "p09_parquet"


def _df(month, n, tag):
    return pd.DataFrame({"year": [2025] * n, "month": [month] * n, "order_id": [f"{tag}{i}" for i in range(n)],
                         "amount": [float(i) for i in range(n)]})


def _read(root):
    return pd.read_parquet(root)


def test_tulis_dan_return(ex, tmp_path):
    root = tmp_path / "sales"
    df = pd.concat([_df(1, 3, "a"), _df(2, 2, "b")])
    parts = ex.write_partitioned(df, root, ["year", "month"])
    check(parts == ["year=2025/month=1", "year=2025/month=2"], f"Return value {parts}.")
    check((root / "year=2025" / "month=1").is_dir(), "Struktur folder harus gaya Hive: year=2025/month=1/.")
    check(len(_read(root)) == 5, "Data yang dibaca ulang tidak 5 baris.")


def test_overwrite_hanya_partisi_terkait(ex, tmp_path):
    root = tmp_path / "sales"
    ex.write_partitioned(pd.concat([_df(1, 3, "a"), _df(2, 2, "b")]), root, ["year", "month"])
    ex.write_partitioned(_df(2, 4, "c"), root, ["year", "month"])
    back = _read(root)
    n1 = (back["month"].astype(int) == 1).sum()
    m2 = back[back["month"].astype(int) == 2]
    check(n1 == 3, f"Partisi month=1 seharusnya tidak tersentuh (3 baris), tersisa {n1}.")
    check(len(m2) == 4 and set(m2["order_id"]) == {"c0", "c1", "c2", "c3"},
          f"Partisi month=2 seharusnya diganti total dengan 4 baris baru, didapat {len(m2)} baris.")


def test_idempotent(ex, tmp_path):
    root = tmp_path / "sales"
    df = _df(3, 5, "x")
    ex.write_partitioned(df, root, ["year", "month"])
    ex.write_partitioned(df, root, ["year", "month"])
    check(len(_read(root)) == 5, "Menulis df yang sama dua kali menggandakan data. Mode overwrite harus idempotent.")


def test_append(ex, tmp_path):
    root = tmp_path / "sales"
    ex.write_partitioned(_df(1, 2, "a"), root, ["year", "month"], mode="append")
    ex.write_partitioned(_df(1, 3, "b"), root, ["year", "month"], mode="append")
    n = len(_read(root))
    check(n == 5, f"Mode append harus menambah data (2 + 3 = 5), didapat {n}. Apakah file lama tertimpa karena namanya sama?")


def test_validasi(ex, tmp_path):
    expect_raises(ValueError, ex.write_partitioned, _df(1, 1, "a"), tmp_path / "x", ["year"], mode="upsert",
                  msg="mode tidak dikenal harus raise ValueError.")
    expect_raises(ValueError, ex.write_partitioned, _df(1, 1, "a"), tmp_path / "x", ["region"],
                  msg="Kolom partisi yang tidak ada harus raise ValueError.")
