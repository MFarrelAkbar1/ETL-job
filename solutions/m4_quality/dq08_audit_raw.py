"""Kunci jawaban DQ08."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from dq07_suite import run_suite

RULES = [
    {"table": "orders", "check": "not_null", "column": "order_id"},
    {"table": "orders", "check": "unique", "columns": ["order_id"], "severity": "warn"},
    {"table": "orders", "check": "not_null", "column": "distributor_id", "severity": "warn"},
    {"table": "orders", "check": "accepted_values", "column": "status",
     "values": ["COMPLETED", "CANCELLED", "PENDING"]},
    {"table": "orders", "check": "accepted_values", "column": "order_date_valid", "values": ["Y"]},
    {"table": "orders", "check": "relationship", "column": "distributor_id",
     "to": "distributors", "field": "distributor_id", "severity": "warn"},
    {"table": "order_items", "check": "unique", "columns": ["order_item_id"]},
    {"table": "order_items", "check": "range", "column": "unit_price", "min": 0.01},
    {"table": "order_items", "check": "not_null", "column": "quantity"},
    {"table": "order_items", "check": "range", "column": "quantity", "min": 1},
    {"table": "order_items", "check": "relationship", "column": "product_code",
     "to": "products", "field": "product_code"},
    {"table": "order_items", "check": "relationship", "column": "order_id",
     "to": "orders", "field": "order_id"},
    {"table": "products", "check": "unique", "columns": ["product_code"]},
    {"table": "distributors", "check": "not_null", "column": "city", "severity": "warn"},
]

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%b-%Y"]


def _read(raw_dir: Path, name: str) -> pd.DataFrame:
    # hanya sel kosong yang NULL; 'N/A' dan sejenisnya tetap terlihat oleh check validity
    return pd.read_csv(raw_dir / f"{name}.csv", dtype=str, keep_default_na=False, na_values=[""])


def _date_valid(s: pd.Series) -> pd.Series:
    parsed = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    for fmt in DATE_FORMATS:
        parsed = parsed.fillna(pd.to_datetime(s, format=fmt, errors="coerce"))
    return parsed.notna().map({True: "Y", False: "N"})


def audit_raw(raw_dir: str | Path) -> pd.DataFrame:
    raw_dir = Path(raw_dir)
    tables = {n: _read(raw_dir, n) for n in ["orders", "order_items", "products", "distributors"]}
    tables["orders"]["order_date_valid"] = _date_valid(tables["orders"]["order_date"])
    return run_suite(tables, RULES)
