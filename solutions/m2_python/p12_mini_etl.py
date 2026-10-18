"""Kunci jawaban P12: mini ETL dari CSV kotor ke star schema."""

from __future__ import annotations

import logging
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from p01_extract import extract_csv
from p02_clean_strings import normalize_product_code
from p03_parse_dates import parse_mixed_dates
from p04_dedup import dedup_latest
from p08_dim_date import build_dim_date

log = logging.getLogger("mini_etl")

UNKNOWN_KEY = -1


def _extract(raw_dir: Path) -> dict[str, pd.DataFrame]:
    names = ["orders", "order_items", "products", "distributors", "regions"]
    return {n: extract_csv(raw_dir / f"{n}.csv").drop(columns="_source_file") for n in names}


def _clean_orders(orders: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    o = dedup_latest(orders, key="order_id", ts_col="updated_at")
    o["order_date"] = parse_mixed_dates(o["order_date"])
    bad = o["order_date"].isna()
    log.info("orders: %d setelah dedup, %d ditolak (tanggal tidak valid)", len(o), int(bad.sum()))
    return o[~bad].reset_index(drop=True), int(bad.sum())


def _dim_product(products: pd.DataFrame) -> pd.DataFrame:
    p = products.copy()
    p["product_id"] = p["product_id"].astype(int)
    p["product_code"] = normalize_product_code(p["product_code"])
    p = p.sort_values("product_id").reset_index(drop=True)
    p.insert(0, "product_key", np.arange(1, len(p) + 1))
    return p[["product_key", "product_id", "product_code", "product_name", "segment", "category", "brand"]]


def _dim_distributor(distributors: pd.DataFrame, regions: pd.DataFrame) -> pd.DataFrame:
    d = distributors.merge(regions[["region_id", "region_name"]], on="region_id", how="left",
                           validate="many_to_one")
    d = d.sort_values("distributor_id").reset_index(drop=True)
    d.insert(0, "distributor_key", np.arange(1, len(d) + 1))
    d["city"] = d["city"].fillna("UNKNOWN")
    cols = ["distributor_key", "distributor_id", "distributor_name", "distributor_type",
            "region_id", "region_name", "city"]
    unknown = pd.DataFrame([{c: "UNKNOWN" for c in cols} | {"distributor_key": UNKNOWN_KEY}])
    return pd.concat([unknown, d[cols]], ignore_index=True)


def _classify_items(items: pd.DataFrame, orders: pd.DataFrame, dim_product: pd.DataFrame) -> pd.DataFrame:
    it = items.copy()
    it["order_item_id"] = it["order_item_id"].astype(int)
    it["product_code"] = normalize_product_code(it["product_code"])
    it["quantity"] = pd.to_numeric(it["quantity"], errors="coerce")
    it["unit_price"] = pd.to_numeric(it["unit_price"], errors="coerce")
    conditions = [
        ~it["order_id"].isin(orders["order_id"]),
        it["unit_price"].isna(),
        it["unit_price"] <= 0,
        it["quantity"].isna(),
        it["quantity"] <= 0,
        ~it["product_code"].isin(dim_product["product_code"]),
    ]
    reasons = ["order_rejected", "unit_price_null", "unit_price_non_positive",
               "quantity_null", "quantity_non_positive", "unknown_product"]
    it["reject_reason"] = np.select(conditions, reasons, default="")
    return it


def run_etl(raw_dir: str | Path, db_path: str | Path) -> dict:
    raw_dir = Path(raw_dir)
    raw = _extract(raw_dir)

    orders, n_bad_orders = _clean_orders(raw["orders"])
    dim_product = _dim_product(raw["products"])
    dim_distributor = _dim_distributor(raw["distributors"], raw["regions"])

    items = _classify_items(raw["order_items"], orders, dim_product)
    rejected = items.loc[items["reject_reason"] != "", ["order_item_id", "order_id", "reject_reason"]]
    good = items[items["reject_reason"] == ""].copy()

    fact = good.merge(orders[["order_id", "order_date", "distributor_id", "status"]],
                      on="order_id", how="inner", validate="many_to_one")
    fact = fact.merge(dim_product[["product_code", "product_key"]], on="product_code",
                      how="left", validate="many_to_one")
    fact = fact.merge(dim_distributor[["distributor_id", "distributor_key"]], on="distributor_id",
                      how="left", validate="many_to_one")
    fact["distributor_key"] = fact["distributor_key"].fillna(UNKNOWN_KEY).astype(int)
    fact["date_key"] = fact["order_date"].dt.strftime("%Y%m%d").astype(int)
    fact["quantity"] = fact["quantity"].astype("int64")
    fact["line_amount"] = fact["quantity"] * fact["unit_price"]
    fact = fact[["order_item_id", "order_id", "date_key", "product_key", "distributor_key",
                 "quantity", "unit_price", "line_amount", "status"]].sort_values("order_item_id")

    fact_dates = pd.to_datetime(fact["date_key"].astype(str), format="%Y%m%d")
    dim_date = build_dim_date(fact_dates.min(), fact_dates.max())

    con = duckdb.connect(str(db_path))
    try:
        con.execute("BEGIN TRANSACTION")
        for name, df in {"dim_product": dim_product, "dim_distributor": dim_distributor,
                         "dim_date": dim_date, "fact_sales": fact,
                         "rejected_order_items": rejected}.items():
            con.register("tmp_df", df)
            con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM tmp_df")
            con.unregister("tmp_df")
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    finally:
        con.close()

    stats = {
        "fact_rows": int(len(fact)),
        "rejected_rows": int(len(rejected)),
        "orders_after_dedup": int(len(orders) + n_bad_orders),
        "orders_rejected": n_bad_orders,
    }
    log.info("ETL selesai: %s", stats)
    return stats
