import numpy as np
import pandas as pd

from py_check import check

EX, FILE = "p03", "p03_parse_dates"


def test_tiga_format(ex):
    s = pd.Series(["2025-03-14", "14/03/2025", "14-Mar-2025", " 2025-01-02 "], index=[5, 6, 7, 8])
    out = ex.parse_mixed_dates(s)
    check(pd.api.types.is_datetime64_any_dtype(out), f"Tipe output harus datetime64, didapat {out.dtype}.")
    check(list(out.index) == [5, 6, 7, 8], "Index output harus sama dengan input.")
    exp = pd.to_datetime(["2025-03-14", "2025-03-14", "2025-03-14", "2025-01-02"])
    got = list(out)
    check(got == list(exp), f"Hasil parse: {[str(x)[:10] for x in got]}, seharusnya semuanya sesuai tanggal aslinya.")


def test_dayfirst(ex):
    out = ex.parse_mixed_dates(pd.Series(["03/04/2025"]))
    check(out.iloc[0] == pd.Timestamp("2025-04-03"),
          f"'03/04/2025' harus 3 April 2025 (format DD/MM/YYYY), didapat {out.iloc[0]}.")


def test_nilai_tidak_valid(ex):
    s = pd.Series(["2025-02-30", "N/A", "00/00/0000", None, np.nan, "2025/03/14", "Mar 14 2025"])
    out = ex.parse_mixed_dates(s)
    check(out.isna().all(),
          "Nilai tidak valid harus menjadi NaT. Yang lolos parse: "
          f"{[(v, str(o)) for v, o in zip(s, out) if not pd.isna(o)]}. Jangan pakai tebakan format otomatis.")


def test_detect_format(ex):
    cases = {"2025-03-14": "%Y-%m-%d", "14/03/2025": "%d/%m/%Y", "14-Mar-2025": "%d-%b-%Y",
             "kemarin": None, None: None}
    for v, e in cases.items():
        got = ex.detect_format(v)
        check(got == e, f"detect_format({v!r}) = {got!r}, seharusnya {e!r}.")


def test_data_asli(ex):
    import duckdb
    from pathlib import Path
    db = Path(__file__).resolve().parents[2] / "data" / "warehouse.duckdb"
    con = duckdb.connect(str(db), read_only=True)
    raw = con.execute("SELECT order_id, order_date FROM orders").df()
    truth = con.execute("SELECT order_id, order_date AS true_date FROM orders_clean").df()
    con.close()
    out = ex.parse_mixed_dates(raw["order_date"])
    m = raw.assign(parsed=out).merge(truth, on="order_id")
    ok = m["parsed"].notna()
    wrong = (m.loc[ok, "parsed"] != pd.to_datetime(m.loc[ok, "true_date"])).sum()
    check(wrong == 0, f"{wrong} tanggal hasil parse tidak sama dengan tanggal sebenarnya.")
    check(ok.mean() > 0.99, f"Hanya {ok.mean():.1%} tanggal yang berhasil di-parse, seharusnya di atas 99%.")
