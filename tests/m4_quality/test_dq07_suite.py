import pandas as pd

from py_check import check, expect_raises

EX, FILE = "dq07", "dq07_suite"

TABLES = {
    "orders": pd.DataFrame({"order_id": ["A", "B", "B", None], "status": ["COMPLETED", "X", "PENDING", "PENDING"],
                            "distributor_id": ["D1", "D2", "D9", None]}),
    "distributors": pd.DataFrame({"distributor_id": ["D1", "D2"]}),
    "items": pd.DataFrame({"qty": [1, 0, 5]}),
}
RULES = [
    {"table": "orders", "check": "not_null", "column": "order_id"},
    {"table": "orders", "check": "unique", "columns": ["order_id"], "severity": "warn"},
    {"table": "orders", "check": "accepted_values", "column": "status", "values": ["COMPLETED", "PENDING"]},
    {"table": "orders", "check": "relationship", "column": "distributor_id", "to": "distributors", "field": "distributor_id"},
    {"table": "items", "check": "range", "column": "qty", "min": 1},
    {"table": "items", "check": "range", "column": "qty", "max": 100, "severity": "warn"},
]


def test_laporan(ex):
    rep = ex.run_suite(TABLES, RULES)
    cols = ["table", "check", "severity", "passed", "failed_rows", "total_rows"]
    check(list(rep.columns) == cols, f"Kolom laporan harus {cols}, didapat {list(rep.columns)}.")
    exp = [
        ("orders", "not_null:order_id", "error", False, 1, 4),
        ("orders", "unique:order_id", "warn", False, 3, 4),
        ("orders", "accepted_values:status", "error", False, 1, 4),
        ("orders", "relationship:distributor_id->distributor_id", "error", False, 1, 4),
        ("items", "range:qty", "error", False, 1, 3),
        ("items", "range:qty", "warn", True, 0, 3),
    ]
    got = [tuple(r) for r in rep.itertuples(index=False)]
    for i, (g, e) in enumerate(zip(got, exp)):
        check(tuple(g) == e, f"Baris laporan ke-{i + 1}: {g}\n  seharusnya: {e}")
    check(len(got) == len(exp), f"Laporan harus {len(exp)} baris, didapat {len(got)}.")


def test_should_block(ex):
    rep = ex.run_suite(TABLES, RULES)
    check(ex.should_block(rep) is True, "Ada pengecekan 'error' yang gagal, pipeline harus diblokir.")
    warn_only = ex.run_suite(TABLES, [RULES[1], RULES[5]])
    check(ex.should_block(warn_only) is False, "Hanya pengecekan 'warn' yang gagal, pipeline tidak boleh diblokir.")


def test_rule_tidak_valid(ex):
    expect_raises(ValueError, ex.run_suite, TABLES, [{"table": "orders", "check": "is_awesome"}],
                  msg="Jenis check tidak dikenal harus raise ValueError.")
    expect_raises(ValueError, ex.run_suite, TABLES, [{"table": "nope", "check": "not_null", "column": "x"}],
                  msg="Tabel yang tidak ada harus raise ValueError.")
