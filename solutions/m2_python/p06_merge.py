"""Kunci jawaban P06."""

from __future__ import annotations

import pandas as pd

from p02_clean_strings import normalize_product_code


def enrich_items(items: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    prod = products[["product_code", "product_name", "segment", "category"]].copy()
    prod["product_code"] = normalize_product_code(prod["product_code"])
    dups = prod["product_code"].duplicated(keep=False)
    if dups.any():
        raise ValueError(f"Master products punya product_code duplikat: {sorted(prod.loc[dups, 'product_code'].unique())}")

    out = items.copy()
    out["product_code"] = normalize_product_code(out["product_code"])
    # validate="many_to_one" membuat pandas error kalau sisi kanan ternyata tidak unik
    out = out.merge(prod, on="product_code", how="left", validate="many_to_one", sort=False)
    out["segment"] = out["segment"].fillna("UNKNOWN")
    out["category"] = out["category"].fillna("UNKNOWN")
    return out


def attach_orders(items: pd.DataFrame, orders: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    if orders["order_id"].duplicated().any():
        raise ValueError("orders punya order_id duplikat. Lakukan deduplikasi dulu.")
    o = orders[["order_id", "order_date", "distributor_id", "status"]]
    out = items.merge(o, on="order_id", how="inner", validate="many_to_one", sort=False)
    return out.reset_index(drop=True), int(len(items) - len(out))
