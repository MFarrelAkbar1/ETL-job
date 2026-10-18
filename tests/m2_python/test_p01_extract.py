from pathlib import Path

import pandas as pd

from py_check import check, expect_raises

EX, FILE = "p01", "p01_extract"
RAW = Path(__file__).resolve().parents[2] / "data" / "raw"

CSV = "id,code,price,tgl,note\n1,007,1.50,2025-01-02,None\n2,,N/A,NA,null\n3,010,2,14/03/2025,NULL\n"


def _write(tmp_path, text, name="sample.csv"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def test_semua_kolom_string(ex, tmp_path):
    df = ex.extract_csv(_write(tmp_path, CSV))
    for c in ["id", "code", "price", "tgl"]:
        non_null = df[c].dropna()
        check(all(isinstance(v, str) for v in non_null),
              f"Kolom '{c}' tidak dibaca sebagai string. Contoh nilai: {list(non_null[:2])}. "
              "Pada tahap extract, jangan biarkan pandas menebak tipe.")
    check(df.loc[0, "code"] == "007", f"'007' berubah menjadi {df.loc[0, 'code']!r}. Leading zero hilang.")
    check(df.loc[0, "price"] == "1.50", f"'1.50' berubah menjadi {df.loc[0, 'price']!r}.")


def test_hanya_null_marker_yang_jadi_nan(ex, tmp_path):
    df = ex.extract_csv(_write(tmp_path, CSV))
    check(pd.isna(df.loc[1, "code"]), "Sel kosong seharusnya menjadi NaN.")
    check(pd.isna(df.loc[1, "price"]) and pd.isna(df.loc[1, "tgl"]), "'N/A' dan 'NA' seharusnya menjadi NaN.")
    check(pd.isna(df.loc[1, "note"]) and pd.isna(df.loc[2, "note"]), "'null' dan 'NULL' seharusnya menjadi NaN.")
    check(df.loc[0, "note"] == "None",
          f"'None' bukan null marker yang diminta, harus tetap string 'None', tetapi menjadi {df.loc[0, 'note']!r}. "
          "Petunjuk: pandas punya daftar NA bawaan.")


def test_source_file(ex, tmp_path):
    df = ex.extract_csv(_write(tmp_path, CSV, "orders.csv"))
    check("_source_file" in df.columns, "Kolom _source_file belum ada.")
    check(set(df["_source_file"]) == {"orders.csv"},
          f"_source_file harus berisi nama file saja, bukan {set(df['_source_file'])}.")


def test_file_tidak_ada(ex, tmp_path):
    missing = tmp_path / "tidak_ada.csv"
    e = expect_raises(FileNotFoundError, ex.extract_csv, missing,
                      msg="File yang tidak ada seharusnya raise FileNotFoundError.")
    check("tidak_ada.csv" in str(e), f"Pesan error harus menyebut path file. Pesan Anda: {e}")


def test_header_saja(ex, tmp_path):
    df = ex.extract_csv(_write(tmp_path, "a,b\n"))
    check(len(df) == 0, "File berisi header saja harus menghasilkan 0 baris.")
    check(list(df.columns) == ["a", "b", "_source_file"],
          f"Kolom seharusnya ['a', 'b', '_source_file'], didapat {list(df.columns)}.")


def test_data_mentah_asli(ex):
    df = ex.extract_csv(RAW / "orders.csv")
    check(len(df) == 50_850, f"orders.csv berisi 50.850 baris data, terbaca {len(df):,}.")
    check(df["order_date"].dropna().map(type).eq(str).all(), "order_date mentah harus tetap string.")
