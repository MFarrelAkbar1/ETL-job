"""Kunci jawaban DQ07."""

from __future__ import annotations

import pandas as pd

from dq01_completeness import check_completeness
from dq02_uniqueness import check_unique
from dq03_validity import check_allowed_values, check_range
from dq04_referential import check_foreign_key


def _run_rule(tables: dict[str, pd.DataFrame], rule: dict):
    if rule["table"] not in tables:
        raise ValueError(f"Tabel tidak ada: {rule['table']}")
    df = tables[rule["table"]]
    kind = rule["check"]
    if kind == "not_null":
        return check_completeness(df, [rule["column"]])[0]
    if kind == "unique":
        return check_unique(df, rule["columns"])
    if kind == "accepted_values":
        return check_allowed_values(df, rule["column"], rule["values"])
    if kind == "range":
        return check_range(df, rule["column"], rule.get("min"), rule.get("max"))
    if kind == "relationship":
        if rule["to"] not in tables:
            raise ValueError(f"Tabel parent tidak ada: {rule['to']}")
        return check_foreign_key(df, rule["column"], tables[rule["to"]], rule["field"])
    raise ValueError(f"Jenis check tidak dikenal: {kind}")


def run_suite(tables: dict[str, pd.DataFrame], rules: list[dict]) -> pd.DataFrame:
    rows = []
    for rule in rules:
        r = _run_rule(tables, rule)
        rows.append({"table": rule["table"], "check": r.check, "severity": rule.get("severity", "error"),
                     "passed": bool(r.passed), "failed_rows": int(r.failed_rows), "total_rows": int(r.total_rows)})
    return pd.DataFrame(rows, columns=["table", "check", "severity", "passed", "failed_rows", "total_rows"])


def should_block(report: pd.DataFrame) -> bool:
    return bool(((~report["passed"]) & (report["severity"] == "error")).any())
