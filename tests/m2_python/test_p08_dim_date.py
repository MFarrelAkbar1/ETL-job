import pandas as pd

from py_check import check, expect_raises

EX, FILE = "p08", "p08_dim_date"
COLS = ["date_key", "date", "year", "quarter", "month", "day", "month_name", "day_of_week",
        "day_name", "week_of_year", "is_weekend", "is_month_end"]


def test_kolom_dan_jumlah(ex):
    d = ex.build_dim_date("2024-02-27", "2024-03-03")
    check(list(d.columns) == COLS, f"Kolom harus {COLS},\n  didapat {list(d.columns)}.")
    check(len(d) == 6, f"2024-02-27 sampai 2024-03-03 = 6 hari (2024 kabisat), didapat {len(d)}.")
    check(list(d["date_key"]) == [20240227, 20240228, 20240229, 20240301, 20240302, 20240303], "date_key salah.")
    check(pd.api.types.is_integer_dtype(d["date_key"]), "date_key harus integer.")
    check(pd.api.types.is_datetime64_any_dtype(d["date"]), "Kolom date harus datetime64.")


def test_nama_indonesia(ex):
    d = ex.build_dim_date("2025-03-14", "2025-03-16").set_index("date_key")
    r = d.loc[20250314]
    check(r["day_name"] == "Jumat" and r["day_of_week"] == 5, f"14 Maret 2025 adalah Jumat (5), didapat {r['day_name']} ({r['day_of_week']}).")
    check(r["month_name"] == "Maret", f"month_name {r['month_name']}, seharusnya 'Maret'.")
    check(d.loc[20250316, "day_of_week"] == 7 and d.loc[20250316, "day_name"] == "Minggu", "Minggu harus day_of_week 7.")
    check(list(d["is_weekend"]) == [False, True, True], "is_weekend salah.")


def test_iso_week_dan_akhir_bulan(ex):
    d = ex.build_dim_date("2024-12-30", "2025-01-01").set_index("date_key")
    check(d.loc[20241230, "week_of_year"] == 1, "30 Des 2024 masuk ISO week 1 tahun 2025.")
    check(bool(d.loc[20241231, "is_month_end"]) and not bool(d.loc[20250101, "is_month_end"]), "is_month_end salah.")
    check(d.loc[20241231, "quarter"] == 4 and d.loc[20250101, "quarter"] == 1, "quarter salah.")


def test_start_lebih_besar(ex):
    expect_raises(ValueError, ex.build_dim_date, "2025-02-01", "2025-01-01",
                  msg="start > end harus raise ValueError.")
