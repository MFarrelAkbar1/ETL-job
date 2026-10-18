"""Test mini ETL. Membandingkan hasil Anda dengan hasil kunci jawaban, ditambah cek struktur."""

from pathlib import Path

import duckdb
import pytest

from py_check import check
from sql_grader import diagnose, frames_match

EX, FILE = "p12", "p12_mini_etl"
RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
TABLES = {
    "dim_product": "product_key",
    "dim_distributor": "distributor_key",
    "dim_date": "date_key",
    "fact_sales": "order_item_id",
    "rejected_order_items": "order_item_id",
}


@pytest.fixture(scope="module")
def expected(tmp_path_factory):
    from py_loader import ROOT, load
    db = tmp_path_factory.mktemp("exp") / "expected.duckdb"
    stats = load(ROOT / "solutions", FILE).run_etl(RAW, db)
    return db, stats


@pytest.fixture(scope="module")
def actual(tmp_path_factory, answers_root):
    from py_loader import load
    db = tmp_path_factory.mktemp("act") / "actual.duckdb"
    mod = load(answers_root, FILE)
    stats = mod.run_etl(RAW, db)
    stats2 = mod.run_etl(RAW, db)  # jalankan dua kali: harus idempotent
    return db, stats, stats2


def _q(db, sql):
    con = duckdb.connect(str(db), read_only=True)
    try:
        return con.execute(sql).df()
    finally:
        con.close()


def test_tabel_dan_kolom(actual, expected):
    for t in TABLES:
        exp_cols = list(_q(expected[0], f"SELECT * FROM {t} LIMIT 0").columns)
        try:
            got = list(_q(actual[0], f"SELECT * FROM {t} LIMIT 0").columns)
        except duckdb.CatalogException:
            pytest.fail(f"Tabel {t} belum dibuat.", pytrace=False)
        check(got == exp_cols, f"Kolom {t} harus {exp_cols},\n  didapat {got}.")


def test_grain_fakta(actual):
    d = _q(actual[0], "SELECT COUNT(*) n, COUNT(DISTINCT order_item_id) u FROM fact_sales")
    check(d.n[0] == d.u[0], f"Grain fact_sales dilanggar: {d.n[0] - d.u[0]} order_item_id duplikat. "
          "Apakah order sudah di-dedup sebelum di-join ke item?")


def test_referential_integrity(actual):
    db = actual[0]
    checks = {
        "product_key": "SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_product d USING (product_key) WHERE d.product_key IS NULL",
        "distributor_key": "SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_distributor d USING (distributor_key) WHERE d.distributor_key IS NULL",
        "date_key": "SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_date d USING (date_key) WHERE d.date_key IS NULL",
    }
    for k, sql in checks.items():
        n = _q(db, sql).iloc[0, 0]
        check(n == 0, f"{n} baris fact_sales punya {k} yang tidak ada di dimensinya (orphan).")
    n_unknown = _q(db, "SELECT COUNT(*) FROM dim_distributor WHERE distributor_key = -1").iloc[0, 0]
    check(n_unknown == 1, "dim_distributor harus punya tepat satu anggota unknown (distributor_key = -1).")


def test_dim_date_tanpa_celah(actual):
    d = _q(actual[0], "SELECT COUNT(*) n, MIN(date) mn, MAX(date) mx FROM dim_date")
    span = (d.mx[0] - d.mn[0]).days + 1
    check(d.n[0] == span, f"dim_date punya {d.n[0]} baris untuk rentang {span} hari. Tidak boleh ada celah atau duplikat.")


def test_rekonsiliasi(actual):
    db = actual[0]
    n_fact = _q(db, "SELECT COUNT(*) FROM fact_sales").iloc[0, 0]
    n_rej = _q(db, "SELECT COUNT(*) FROM rejected_order_items").iloc[0, 0]
    n_raw = sum(1 for _ in open(RAW / "order_items.csv", encoding="utf-8")) - 1
    check(n_fact + n_rej == n_raw,
          f"Rekonsiliasi gagal: fact {n_fact:,} + rejected {n_rej:,} = {n_fact + n_rej:,}, sedangkan item mentah {n_raw:,}. "
          "Setiap baris sumber harus berakhir di fakta ATAU di tabel reject.")


def test_idempotent(actual):
    check(actual[1] == actual[2], f"run_etl dua kali memberi statistik berbeda: {actual[1]} vs {actual[2]}.")


def test_stats(actual, expected):
    for k, v in expected[1].items():
        check(actual[1].get(k) == v, f"stats['{k}'] = {actual[1].get(k)}, seharusnya {v}.")


@pytest.mark.parametrize("table", list(TABLES))
def test_isi_tabel(actual, expected, table):
    key = TABLES[table]
    e = _q(expected[0], f"SELECT * FROM {table} ORDER BY {key}")
    u = _q(actual[0], f"SELECT * FROM {table} ORDER BY {key}")
    if not frames_match(u, e, ordered=True):
        msgs = diagnose(u, e, ordered=True)
        pytest.fail(f"Isi {table} belum sesuai:\n" + "\n".join(f"- {m}" for m in msgs), pytrace=False)
