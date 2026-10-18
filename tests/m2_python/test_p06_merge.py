import numpy as np
import pandas as pd

from py_check import check, expect_raises

EX, FILE = "p06", "p06_merge"

PRODUCTS = pd.DataFrame({
    "product_code": ["PRD-0001", "PRD-0002", "PRD-0003"],
    "product_name": ["Paramex", "Rinso", "Milo"],
    "segment": ["Farmasi", "Consumer Goods", "Consumer Goods"],
    "category": ["Obat Bebas", "Rumah Tangga", "Makanan dan Minuman"],
    "unit_price": [5000.0, 20000.0, 15000.0],
})


def _items():
    return pd.DataFrame({
        "order_item_id": [1, 2, 3, 4, 5],
        "order_id": ["O1", "O1", "O2", "O3", "O9"],
        "product_code": [" prd-0002", "PRD-0001 ", "PRD-0002", "PRD-9999", "prd-0003"],
        "quantity": [1, 2, 3, 4, 5],
    })


def test_enrich(ex):
    out = ex.enrich_items(_items(), PRODUCTS)
    check(len(out) == 5, f"Jumlah baris berubah dari 5 menjadi {len(out)}.")
    check(list(out["order_item_id"]) == [1, 2, 3, 4, 5], "Urutan baris items harus dipertahankan.")
    check(list(out["product_code"])[:2] == ["PRD-0002", "PRD-0001"], "product_code di output harus sudah dinormalisasi.")
    for c in ["product_name", "segment", "category"]:
        check(c in out.columns, f"Kolom {c} belum ada.")
    check(list(out["product_name"])[:3] == ["Rinso", "Paramex", "Rinso"], "product_name tidak cocok; normalisasi kode sebelum merge?")
    row = out[out["order_item_id"] == 4].iloc[0]
    check(row["segment"] == "UNKNOWN" and row["category"] == "UNKNOWN" and pd.isna(row["product_name"]),
          "Item dengan kode tidak dikenal harus tetap ada, segment/category 'UNKNOWN', product_name NaN.")


def test_master_duplikat(ex):
    dup = pd.concat([PRODUCTS, PRODUCTS.iloc[[0]].assign(product_code="prd-0001 ")], ignore_index=True)
    e = expect_raises(ValueError, ex.enrich_items, _items(), dup,
                      msg="Master products dengan kode duplikat (setelah normalisasi) harus raise ValueError, "
                          "karena merge akan menggandakan baris fakta.")
    check("duplikat" in str(e).lower(), f"Pesan ValueError harus mengandung kata 'duplikat'. Pesan Anda: {e}")


def test_attach_orders(ex):
    orders = pd.DataFrame({"order_id": ["O1", "O2", "O3"], "order_date": pd.to_datetime(["2025-01-01"] * 3),
                           "distributor_id": ["D001", None, "D002"], "status": ["COMPLETED"] * 3, "channel": ["x"] * 3})
    out, n_drop = ex.attach_orders(_items(), orders)
    check(n_drop == 1, f"Satu item (order O9) seharusnya terbuang, fungsi melaporkan {n_drop}.")
    check(len(out) == 4 and list(out["order_item_id"]) == [1, 2, 3, 4], "Hasil inner join atau urutannya belum benar.")
    check({"order_date", "distributor_id", "status"} <= set(out.columns), "Kolom order_date, distributor_id, status belum ditambahkan.")
    check("channel" not in out.columns, "Hanya order_date, distributor_id, status yang ditambahkan dari orders.")
    check(list(out.index) == [0, 1, 2, 3], "Index harus di-reset.")


def test_attach_orders_duplikat(ex):
    orders = pd.DataFrame({"order_id": ["O1", "O1"], "order_date": [np.nan] * 2,
                           "distributor_id": ["D1", "D1"], "status": ["A", "B"]})
    expect_raises(ValueError, ex.attach_orders, _items(), orders,
                  msg="orders dengan order_id duplikat harus raise ValueError.")
