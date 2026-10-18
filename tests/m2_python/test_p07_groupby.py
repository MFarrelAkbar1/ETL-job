import pandas as pd

from py_check import check

EX, FILE = "p07", "p07_groupby"


def _sales():
    return pd.DataFrame({
        "order_id": ["O1", "O1", "O2", "O3", "O4", "O5"],
        "order_date": pd.to_datetime(["2025-01-05", "2025-01-05", "2025-01-20", "2025-02-01", "2025-01-07", "2025-02-11"]),
        "status": ["COMPLETED", "COMPLETED", "COMPLETED", "COMPLETED", "CANCELLED", "COMPLETED"],
        "segment": ["Farmasi", "Farmasi", "Farmasi", "Consumer Goods", "Farmasi", "Farmasi"],
        "line_amount": [100.0, 50.0, 200.0, 80.0, 999.0, 10.005],
    })


def test_monthly(ex):
    out = ex.monthly_revenue_by_segment(_sales())
    cols = ["month", "segment", "revenue", "n_orders", "avg_order_value"]
    check(list(out.columns) == cols, f"Kolom harus {cols}, didapat {list(out.columns)}.")
    check(list(out["month"]) == ["2025-01", "2025-02", "2025-02"], f"month/urutan salah: {list(out['month'])}.")
    jan = out.iloc[0]
    check(jan["revenue"] == 350.0, f"Revenue Farmasi Januari {jan['revenue']}, apakah order CANCELLED ikut dihitung?")
    check(jan["n_orders"] == 2, f"n_orders Januari {jan['n_orders']}, seharusnya 2 order unik (bukan jumlah baris).")
    check(jan["avg_order_value"] == 175.0, f"avg_order_value Januari {jan['avg_order_value']}, seharusnya revenue / n_orders.")
    check(list(out["segment"])[1:] == ["Consumer Goods", "Farmasi"], "Dalam bulan yang sama urutkan berdasarkan segment.")
    check(out.iloc[2]["revenue"] == 10.01 or out.iloc[2]["revenue"] == 10.0, "revenue harus dibulatkan 2 desimal.")


def test_top_n(ex):
    df = pd.DataFrame({"cat": ["a", "a", "a", "a", "b", "b"], "item": ["x1", "x2", "x3", "x4", "y1", "y2"],
                       "val": [5, 9, 9, 1, 3, 7]})
    out = ex.top_n_per_group(df, "cat", "val", n=2)
    check(list(out.columns) == ["cat", "item", "val", "rank"], f"Kolom harus ['cat', 'item', 'val', 'rank'], didapat {list(out.columns)}.")
    check(list(out["item"]) == ["x2", "x3", "y2", "y1"],
          f"Urutan item {list(out['item'])}. Seri (x2 dan x3 = 9) dimenangkan yang muncul lebih dulu.")
    check(list(out["rank"]) == [1, 2, 1, 2], f"rank {list(out['rank'])}, seharusnya [1, 2, 1, 2].")
    check(list(out.index) == [0, 1, 2, 3], "Index harus di-reset.")
