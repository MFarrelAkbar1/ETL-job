from datetime import datetime, timedelta

import pandas as pd

from dq_helpers import check_result
from py_check import check, expect_raises

EX, FILE = "dq05", "dq05_freshness"
NOW = datetime(2025, 11, 3, 6, 0, 0)


def test_segar(ex):
    df = pd.DataFrame({"updated_at": ["2025-11-02 20:00:00", "2025-11-03 02:30:00", "bukan tanggal", None]})
    r = ex.check_freshness(df, "updated_at", timedelta(hours=6), NOW)
    check_result(r, "freshness:updated_at", True, 0, 4, "data terbaru 3,5 jam lalu, batas 6 jam")
    check(r.details.get("latest") == "2025-11-03T02:30:00", f"details['latest'] = {r.details.get('latest')!r}.")
    check(r.details.get("age_hours") == 3.5, f"details['age_hours'] = {r.details.get('age_hours')}, seharusnya 3.5.")


def test_basi(ex):
    df = pd.DataFrame({"updated_at": pd.to_datetime(["2025-11-01 23:00:00"])})
    r = ex.check_freshness(df, "updated_at", timedelta(hours=24), NOW)
    check_result(r, "freshness:updated_at", False, 1, 1, "data terbaru 31 jam lalu, batas 24 jam")


def test_kosong(ex):
    r = ex.check_freshness(pd.DataFrame({"updated_at": []}), "updated_at", timedelta(hours=1), NOW)
    check(not r.passed, "Tabel tanpa timestamp valid tidak boleh dianggap segar.")
    check(r.details.get("latest") is None, "details['latest'] harus None kalau tidak ada timestamp valid.")


def test_volume(ex):
    hist = [1000, 1100, 950, 5000, 1050]  # 5000 = satu hari anomali, median tidak terpengaruh
    r = ex.check_volume(400, hist)
    check_result(r, "volume", False, 1, 400, "volume turun drastis")
    check(r.details.get("expected") == 1050, f"expected = {r.details.get('expected')}, seharusnya median 1050 (bukan rata-rata).")
    check(r.details.get("deviation_pct") == -61.9, f"deviation_pct = {r.details.get('deviation_pct')}, seharusnya -61.9.")
    check(ex.check_volume(1200, hist).passed, "1200 vs median 1050 (+14%) masih dalam toleransi 30%.")
    expect_raises(ValueError, ex.check_volume, 10, [], msg="history kosong harus raise ValueError.")
