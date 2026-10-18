"""Generator dataset simulasi perusahaan consumer goods dan farmasi.

Jalankan:  python data/generate.py

Output:
  data/raw/*.csv           data mentah (kotor), dipakai Modul 2
  data/parquet/*.parquet   salinan Parquet dari tabel yang sama
  data/warehouse.duckdb    semua tabel mentah + tabel bersih + tabel bantu soal SQL

Seed tetap, jadi hasilnya selalu sama di setiap mesin.

Catatan belajar: bagian "INJEKSI DATA KOTOR" di bawah menunjukkan jenis kotoran
yang disisipkan. Kalau ingin tantangan penuh, jangan baca bagian itu sebelum
mengerjakan soal cleaning. Kamus data ada di data/KAMUS_DATA.md.
"""

from __future__ import annotations

import shutil
from datetime import date, datetime, timedelta
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

SEED = 42
ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "raw"
PARQUET_DIR = ROOT / "parquet"
DB_PATH = ROOT / "warehouse.duckdb"

N_ORDERS = 50_000
START = date(2024, 1, 1)
END = date(2025, 12, 31)

rng = np.random.default_rng(SEED)


# --------------------------------------------------------------------------
# Master data
# --------------------------------------------------------------------------
def make_regions() -> pd.DataFrame:
    rows = [
        ("R01", "DKI Jakarta", "Jawa"),
        ("R02", "Jawa Barat", "Jawa"),
        ("R03", "Jawa Tengah", "Jawa"),
        ("R04", "Jawa Timur", "Jawa"),
        ("R05", "Bali dan Nusa Tenggara", "Bali Nusra"),
        ("R06", "Sumatera Utara", "Sumatera"),
        ("R07", "Sumatera Selatan", "Sumatera"),
        ("R08", "Kalimantan", "Kalimantan"),
        ("R09", "Sulawesi", "Sulawesi"),
        ("R10", "Papua dan Maluku", "Papua Maluku"),  # sengaja tanpa distributor
    ]
    return pd.DataFrame(rows, columns=["region_id", "region_name", "island_group"])


CITIES = {
    "R01": ["Jakarta Pusat", "Jakarta Barat", "Jakarta Timur", "Jakarta Selatan"],
    "R02": ["Bandung", "Bekasi", "Bogor", "Cirebon"],
    "R03": ["Semarang", "Solo", "Tegal"],
    "R04": ["Surabaya", "Malang", "Kediri", "Jember"],
    "R05": ["Denpasar", "Mataram", "Kupang"],
    "R06": ["Medan", "Pematangsiantar"],
    "R07": ["Palembang", "Lubuklinggau"],
    "R08": ["Balikpapan", "Banjarmasin", "Pontianak"],
    "R09": ["Makassar", "Manado"],
}
STREETS = ["Sudirman", "Gatot Subroto", "Diponegoro", "Ahmad Yani", "Merdeka",
           "Pahlawan", "Veteran", "Gajah Mada", "Hayam Wuruk", "Siliwangi"]
NAME_A = ["Sinar", "Mitra", "Sumber", "Cahaya", "Prima", "Karya", "Bina", "Nusa", "Mega", "Sentosa"]
NAME_B = ["Medika", "Farma", "Niaga", "Distribusi", "Sehat", "Makmur", "Abadi", "Jaya"]
DIST_TYPES = ["PBF", "Grosir", "Apotek Chain", "Modern Trade"]


def make_distributors() -> pd.DataFrame:
    region_ids = list(CITIES.keys())
    # bobot region supaya Jawa lebih ramai
    w = np.array([5, 5, 3, 5, 2, 2, 2, 2, 1], dtype=float)
    w /= w.sum()
    rows = []
    for i in range(1, 81):
        rid = rng.choice(region_ids, p=w)
        city = rng.choice(CITIES[rid])
        name = f"PT {rng.choice(NAME_A)} {rng.choice(NAME_B)} {i:02d}"
        addr = f"Jl. {rng.choice(STREETS)} No. {int(rng.integers(1, 200))}"
        onboard = date(2020, 1, 1) + timedelta(days=int(rng.integers(0, 4 * 365)))
        rows.append(dict(
            distributor_id=f"D{i:03d}", distributor_name=name, distributor_type=rng.choice(DIST_TYPES),
            region_id=rid, city=city, address=addr, onboard_date=onboard,
            is_active=bool(rng.random() > 0.08),
        ))
    return pd.DataFrame(rows)


CATEGORIES = {
    "Farmasi": {
        "Obat Bebas": ["Paramex", "Bodrex", "Sanmol", "Tolak Angin"],
        "Obat Resep": ["Amoxsan", "Cefadroxil Hexpharm", "Metformin Novell"],
        "Vitamin dan Suplemen": ["Enervon", "Imboost", "Redoxon", "Sangobion"],
    },
    "Consumer Goods": {
        "Perawatan Diri": ["Lifebuoy", "Pepsodent", "Sunsilk", "Biore"],
        "Makanan dan Minuman": ["Indomie", "Teh Pucuk", "Milo", "Roma"],
        "Rumah Tangga": ["Rinso", "Sunlight", "Baygon", "So Klin"],
    },
}
VARIANTS = ["Strip 10", "Botol 60ml", "Box 12", "Sachet", "Pouch 800g", "Tube 75g", "Kaleng", "Refill 1L"]


def make_products() -> pd.DataFrame:
    rows = []
    pid = 1
    for segment, cats in CATEGORIES.items():
        n_per_cat = 20 if segment == "Farmasi" else 30
        for cat, brands in cats.items():
            for _ in range(n_per_cat):
                brand = rng.choice(brands)
                if segment == "Farmasi":
                    price = int(rng.integers(5, 250)) * 1000
                else:
                    price = int(rng.integers(3, 80)) * 1000
                rows.append(dict(
                    product_id=pid, product_code=f"PRD-{pid:04d}",
                    product_name=f"{brand} {rng.choice(VARIANTS)}",
                    segment=segment, category=cat, brand=brand, unit_price=float(price),
                    is_active=bool(rng.random() > 0.1),
                    launch_date=date(2019, 1, 1) + timedelta(days=int(rng.integers(0, 5 * 365))),
                ))
                pid += 1
    df = pd.DataFrame(rows)  # 3 x 20 Farmasi + 3 x 30 Consumer Goods = 150 produk
    assert len(df) == 150
    return df


# --------------------------------------------------------------------------
# Transaksi (versi BENAR / ground truth)
# --------------------------------------------------------------------------
def make_orders(distributors: pd.DataFrame) -> pd.DataFrame:
    n_days = (END - START).days + 1
    # musiman ringan: lebih ramai menjelang akhir tahun
    day_idx = np.arange(n_days)
    days = [START + timedelta(days=int(d)) for d in day_idx]
    month = np.array([d.month for d in days])
    w_day = 1.0 + 0.25 * np.isin(month, [11, 12]) + 0.1 * np.sin(day_idx / 30)
    w_day /= w_day.sum()

    dist_ids = distributors["distributor_id"].to_numpy()
    w_dist = rng.lognormal(0, 0.8, size=len(dist_ids))
    w_dist /= w_dist.sum()

    chosen_days = rng.choice(day_idx, size=N_ORDERS, p=w_day)
    chosen_dist = rng.choice(dist_ids, size=N_ORDERS, p=w_dist).astype(object)

    # distributor yatim (tidak ada di master) dan null
    n_orphan = int(N_ORDERS * 0.006)
    orphan_pos = rng.choice(N_ORDERS, size=n_orphan, replace=False)
    chosen_dist[orphan_pos] = rng.choice(["D901", "D902", "D903", "D904", "D905"], size=n_orphan)
    rest = np.setdiff1d(np.arange(N_ORDERS), orphan_pos)
    null_pos = rng.choice(rest, size=int(N_ORDERS * 0.002), replace=False)
    chosen_dist[null_pos] = None

    order_dates = [START + timedelta(days=int(d)) for d in chosen_days]
    status = rng.choice(["COMPLETED", "CANCELLED", "PENDING"], size=N_ORDERS, p=[0.90, 0.06, 0.04])
    channel = rng.choice(["Sales Rep", "E-Order", "Telesales"], size=N_ORDERS, p=[0.5, 0.35, 0.15])
    hours = rng.integers(8, 20 * 24, size=N_ORDERS)  # update terakhir 8 jam s.d. 20 hari setelah order

    df = pd.DataFrame({
        "order_date": order_dates,
        "distributor_id": chosen_dist,
        "status": status,
        "channel": channel,
    })
    df = df.sort_values(["order_date"], kind="stable").reset_index(drop=True)
    df.insert(0, "order_id", [f"ORD-{i:06d}" for i in range(1, N_ORDERS + 1)])
    df["updated_at"] = [datetime.combine(d, datetime.min.time()) + timedelta(hours=int(h))
                        for d, h in zip(df["order_date"], hours)]
    return df


def make_order_items(orders: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    # 8 produk terakhir tidak pernah dipesan (untuk soal anti join)
    orderable = products[products["product_id"] <= 142]
    codes = orderable["product_code"].to_numpy()
    prices = dict(zip(products["product_code"], products["unit_price"]))
    seg = dict(zip(products["product_code"], products["category"]))
    w = rng.lognormal(0, 1.0, size=len(codes))
    w /= w.sum()

    n_items = rng.integers(1, 6, size=len(orders))
    order_ids = np.repeat(orders["order_id"].to_numpy(), n_items)
    rows_codes = []
    for k in n_items:
        rows_codes.extend(rng.choice(codes, size=int(k), replace=False, p=w))
    qty = []
    for c in rows_codes:
        if seg[c] == "Obat Resep":
            qty.append(int(rng.integers(1, 11)))
        else:
            qty.append(int(rng.integers(1, 51)))
    df = pd.DataFrame({
        "order_item_id": np.arange(1, len(order_ids) + 1),
        "order_id": order_ids,
        "product_code": rows_codes,
        "quantity": qty,
    })
    df["unit_price"] = df["product_code"].map(prices).astype(float)
    df["line_amount"] = (df["quantity"] * df["unit_price"]).astype(float)
    return df


def make_returns(orders: pd.DataFrame, items: pd.DataFrame) -> pd.DataFrame:
    comp = orders.loc[orders["status"] == "COMPLETED", ["order_id", "order_date"]]
    cand = items.merge(comp, on="order_id")
    pick = cand.sample(frac=0.03, random_state=SEED).sort_values("order_item_id")
    ret_qty = [int(rng.integers(1, q + 1)) for q in pick["quantity"]]
    reasons = rng.choice(["Kemasan rusak", "Kedaluwarsa", "Salah kirim", "Kelebihan stok"],
                         size=len(pick), p=[0.35, 0.25, 0.25, 0.15])
    ret_dates = [d + timedelta(days=int(rng.integers(3, 31))) for d in pick["order_date"]]
    df = pd.DataFrame({
        "return_id": [f"RET-{i:05d}" for i in range(1, len(pick) + 1)],
        "order_id": pick["order_id"].to_numpy(),
        "order_item_id": pick["order_item_id"].to_numpy(),
        "product_code": pick["product_code"].to_numpy(),
        "return_qty": ret_qty,
        "return_date": ret_dates,
        "reason": reasons,
    })
    df["refund_amount"] = (df["return_qty"] * pick["unit_price"].to_numpy()).astype(float)
    return df


# --------------------------------------------------------------------------
# INJEKSI DATA KOTOR
# --------------------------------------------------------------------------
DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%b-%Y"]


def fmt_date(d: date, fmt: str) -> str:
    # %b dibuat eksplisit bahasa Inggris supaya tidak tergantung locale mesin
    if fmt == "%d-%b-%Y":
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return f"{d.day:02d}-{months[d.month - 1]}-{d.year}"
    return d.strftime(fmt)


def dirty_orders(orders: pd.DataFrame) -> pd.DataFrame:
    df = orders.copy()
    n = len(df)
    fmt_choice = rng.choice(len(DATE_FORMATS), size=n, p=[0.75, 0.15, 0.10])
    df["order_date"] = [fmt_date(d, DATE_FORMATS[k]) for d, k in zip(df["order_date"], fmt_choice)]

    # duplikat: versi lama dari order yang sama (status lama, updated_at lebih awal)
    dup_idx = rng.choice(n, size=int(n * 0.015), replace=False)
    old = df.iloc[dup_idx].copy()
    old["status"] = "PENDING"
    old["updated_at"] = old["updated_at"] - pd.to_timedelta(rng.integers(1, 8, size=len(old)), unit="h")
    old_fmt = rng.choice(len(DATE_FORMATS), size=len(old))
    true_dates = orders.iloc[dup_idx]["order_date"].to_numpy()
    old["order_date"] = [fmt_date(d, DATE_FORMATS[k]) for d, k in zip(true_dates, old_fmt)]
    # duplikat identik (baris terkirim dua kali)
    exact_idx = rng.choice(np.setdiff1d(np.arange(n), dup_idx), size=100, replace=False)
    exact = df.iloc[exact_idx].copy()

    # tanggal hilang atau rusak, hanya pada order yang tidak punya duplikat
    clean_pool = np.setdiff1d(np.arange(n), np.concatenate([dup_idx, exact_idx]))
    bad_idx = rng.choice(clean_pool, size=int(n * 0.005), replace=False)
    bad_vals = rng.choice(["", "N/A", "00/00/0000"], size=len(bad_idx)).astype(object)
    bad_vals[bad_vals == ""] = None
    df.loc[bad_idx, "order_date"] = bad_vals

    out = pd.concat([df, old, exact], ignore_index=True)
    out = out.sample(frac=1.0, random_state=SEED).reset_index(drop=True)
    return out


def dirty_items(items: pd.DataFrame) -> pd.DataFrame:
    df = items.drop(columns=["line_amount"]).copy()
    n = len(df)
    codes = df["product_code"].to_numpy().astype(object)
    v = rng.random(n)
    codes = np.where(v < 0.10, np.char.lower(codes.astype(str)), codes)
    codes = np.where((v >= 0.10) & (v < 0.18), np.char.add(np.char.add(" ", codes.astype(str)), " "), codes)
    codes = np.where((v >= 0.18) & (v < 0.22), np.char.add(np.char.lower(codes.astype(str)), " "), codes)
    df["product_code"] = codes

    price = df["unit_price"].to_numpy().copy()
    neg = rng.random(n) < 0.004
    price[neg] = -price[neg]
    nul = (rng.random(n) < 0.003) & ~neg
    price[nul] = np.nan
    df["unit_price"] = price

    qty = df["quantity"].astype("Int64")
    qnull = (rng.random(n) < 0.002) & ~neg & ~nul
    qty[qnull] = pd.NA
    df["quantity"] = qty
    return df


def dirty_distributors(d: pd.DataFrame) -> pd.DataFrame:
    df = d.copy()
    df.loc[df.index[[4, 22, 57]], "city"] = None
    return df


# --------------------------------------------------------------------------
# Tabel bantu untuk soal SQL tertentu
# --------------------------------------------------------------------------
def make_recon(orders: pd.DataFrame, items: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """stg_sales (sumber) vs dwh_sales (target) untuk Juni 2025."""
    amt = items.groupby("order_id", as_index=False)["line_amount"].sum().rename(columns={"line_amount": "amount"})
    src = orders[(orders["status"] == "COMPLETED")
                 & (pd.to_datetime(orders["order_date"]).dt.strftime("%Y-%m") == "2025-06")]
    src = src[["order_id", "order_date"]].merge(amt, on="order_id")
    src = src.sort_values("order_id").reset_index(drop=True)

    tgt = src.copy()
    d = lambda s: date.fromisoformat(s)  # noqa: E731
    # 1) baris hilang pada 3 tanggal
    for day, k in [("2025-06-05", 4), ("2025-06-14", 1), ("2025-06-27", 7)]:
        idx = tgt.index[tgt["order_date"] == d(day)][:k]
        tgt = tgt.drop(idx)
    # 2) baris dobel pada 1 tanggal
    dup = tgt[tgt["order_date"] == d("2025-06-20")].head(2)
    tgt = pd.concat([tgt, dup])
    # 3) nilai berubah pada 1 tanggal (jumlah baris sama)
    i = tgt.index[tgt["order_date"] == d("2025-06-11")][0]
    tgt.loc[i, "amount"] = tgt.loc[i, "amount"] + 125_000
    # 4) seluruh tanggal 30 Juni belum termuat
    tgt = tgt[tgt["order_date"] != d("2025-06-30")]
    # 5) satu tanggal yang hanya ada di target (salah muat)
    extra = src[src["order_date"] == d("2025-06-02")].head(3).copy()
    extra["order_date"] = d("2025-05-31")
    extra["order_id"] = extra["order_id"] + "-X"
    tgt = pd.concat([tgt, extra]).sort_values(["order_date", "order_id"]).reset_index(drop=True)
    return src, tgt


def make_product_merge(products: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    dim = products[["product_id", "product_code", "product_name", "category", "unit_price", "is_active"]].copy()
    dim["updated_at"] = pd.Timestamp("2025-12-01 00:00:00")
    # beberapa produk di target sudah di-update lebih baru oleh proses lain
    dim.loc[dim["product_id"].isin([12, 77]), "updated_at"] = pd.Timestamp("2026-01-10 09:00:00")

    up = []
    ts = pd.Timestamp("2026-01-05 02:00:00")
    for pid in [3, 18, 25, 40, 66, 90, 101, 133]:  # update harga
        r = dim[dim["product_id"] == pid].iloc[0]
        up.append(dict(product_id=pid, product_code=r.product_code, product_name=r.product_name,
                       category=r.category, unit_price=float(round(r.unit_price * 1.08, -2)),
                       is_active=bool(r.is_active), op="U", updated_at=ts))
    for pid in [12, 77]:  # update yang lebih lama dari target: harus diabaikan
        r = dim[dim["product_id"] == pid].iloc[0]
        up.append(dict(product_id=pid, product_code=r.product_code, product_name=r.product_name + " (lama)",
                       category=r.category, unit_price=float(r.unit_price - 1000),
                       is_active=bool(r.is_active), op="U", updated_at=ts))
    for pid in [55, 140]:  # dinonaktifkan via update
        r = dim[dim["product_id"] == pid].iloc[0]
        up.append(dict(product_id=pid, product_code=r.product_code, product_name=r.product_name,
                       category=r.category, unit_price=float(r.unit_price), is_active=False, op="U", updated_at=ts))
    for pid in [147, 149]:  # dihapus
        r = dim[dim["product_id"] == pid].iloc[0]
        up.append(dict(product_id=pid, product_code=r.product_code, product_name=r.product_name,
                       category=r.category, unit_price=float(r.unit_price), is_active=bool(r.is_active),
                       op="D", updated_at=ts))
    up.append(dict(product_id=999, product_code="PRD-0999", product_name="Tidak Ada",
                   category="Obat Bebas", unit_price=1000.0, is_active=True, op="D", updated_at=ts))
    new = [(151, "Sanmol Forte Strip 10", "Obat Bebas", 18000.0),
           (152, "Imboost Kids Botol 60ml", "Vitamin dan Suplemen", 54000.0),
           (153, "Rinso Matic Refill 1L", "Rumah Tangga", 32000.0)]
    for pid, name, cat, price in new:
        up.append(dict(product_id=pid, product_code=f"PRD-{pid:04d}", product_name=name, category=cat,
                       unit_price=price, is_active=True, op="I", updated_at=ts))
    return dim, pd.DataFrame(up)


def make_scd2(distributors: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = distributors[["distributor_id", "distributor_name", "region_id", "city", "address"]].copy()
    dim = base.copy()
    dim.insert(0, "distributor_sk", np.arange(1, len(dim) + 1))
    dim["valid_from"] = date(2024, 1, 1)
    dim["valid_to"] = date(9999, 12, 31)
    dim["is_current"] = True

    snap = base.copy().set_index("distributor_id")
    # perubahan atribut SCD2 (region/city/address)
    snap.loc["D003", ["region_id", "city"]] = ["R04", "Surabaya"]
    snap.loc["D010", "address"] = "Jl. Pemuda No. 8"
    snap.loc["D017", ["region_id", "city", "address"]] = ["R02", "Bandung", "Jl. Asia Afrika No. 21"]
    snap.loc["D029", "address"] = "Jl. Kartini No. 3"
    snap.loc["D041", "city"] = snap.loc["D041", "city"]  # tidak berubah
    snap.loc["D044", "address"] = "Jl. Imam Bonjol No. 50"
    snap.loc["D062", ["region_id", "city"]] = ["R08", "Balikpapan"]
    # city NULL berubah jadi terisi (jebakan perbandingan NULL)
    null_city_ids = distributors.loc[distributors["city"].isna(), "distributor_id"].tolist()
    if null_city_ids:
        snap.loc[null_city_ids[0], "city"] = "Kota Baru"
    # perubahan nama saja: SCD Type 1 (timpa di baris current, tanpa versi baru)
    snap.loc["D020", "distributor_name"] = snap.loc["D020", "distributor_name"] + " Tbk"
    snap.loc["D051", "distributor_name"] = "PT Mega Farma Nusantara 51"
    # perubahan nama + region sekaligus
    snap.loc["D070", ["distributor_name", "region_id", "city"]] = ["PT Prima Sehat Indonesia 70", "R09", "Makassar"]
    # dua distributor tidak muncul di snapshot: JANGAN ditutup
    snap = snap.drop(index=["D033", "D078"])
    snap = snap.reset_index()
    newd = pd.DataFrame([
        ("D081", "PT Cahaya Medika 81", "R01", "Jakarta Utara", "Jl. Pluit No. 1"),
        ("D082", "PT Nusa Farma 82", "R06", "Medan", "Jl. Gatot Subroto No. 77"),
        ("D083", "PT Karya Niaga 83", "R09", "Manado", None),
    ], columns=snap.columns)
    snap = pd.concat([snap, newd], ignore_index=True)
    return dim, snap


def make_dist_history(distributors: pd.DataFrame) -> pd.DataFrame:
    """SCD2 historis: region_id saat ini sama dengan master distributors."""
    region_ids = list(CITIES.keys())
    rows = []
    sk = 1
    ids = distributors["distributor_id"].tolist()
    two_ver = set(ids[5:20])      # pindah region pada 2025-01-01
    three_ver = set(ids[30:35])   # pindah region 2024-07-01 dan 2025-04-01
    for _, r in distributors.iterrows():
        cur = r["region_id"]
        others = [x for x in region_ids if x != cur]
        if r["distributor_id"] in two_ver:
            old = rng.choice(others)
            versions = [(old, r["onboard_date"], date(2025, 1, 1)), (cur, date(2025, 1, 1), date(9999, 12, 31))]
        elif r["distributor_id"] in three_ver:
            a, b = rng.choice(others, size=2, replace=False)
            versions = [(a, r["onboard_date"], date(2024, 7, 1)), (b, date(2024, 7, 1), date(2025, 4, 1)),
                        (cur, date(2025, 4, 1), date(9999, 12, 31))]
        else:
            versions = [(cur, r["onboard_date"], date(9999, 12, 31))]
        for reg, vf, vt in versions:
            rows.append(dict(distributor_sk=sk, distributor_id=r["distributor_id"],
                             distributor_name=r["distributor_name"], region_id=reg,
                             valid_from=vf, valid_to=vt, is_current=vt == date(9999, 12, 31)))
            sk += 1
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
def main() -> None:
    regions = make_regions()
    distributors_true = make_distributors()
    products = make_products()
    orders_true = make_orders(distributors_true)
    items_true = make_order_items(orders_true, products)
    returns = make_returns(orders_true, items_true)

    orders_raw = dirty_orders(orders_true)
    items_raw = dirty_items(items_true)
    distributors = dirty_distributors(distributors_true)

    stg_sales, dwh_sales = make_recon(orders_true, items_true)
    dim_product, product_updates = make_product_merge(products)
    dim_scd2, dist_snapshot = make_scd2(distributors)
    dist_hist = make_dist_history(distributors)

    raw_tables = {
        "regions": regions,
        "distributors": distributors,
        "products": products,
        "orders": orders_raw,
        "order_items": items_raw,
        "returns": returns,
    }
    clean_tables = {
        "orders_clean": orders_true,
        "order_items_clean": items_true,
    }
    helper_tables = {
        "stg_sales": stg_sales,
        "dwh_sales": dwh_sales,
        "dim_product": dim_product,
        "product_updates": product_updates,
        "dim_distributor_scd2": dim_scd2,
        "distributor_snapshot": dist_snapshot,
        "dim_distributor_hist": dist_hist,
    }

    for d in (RAW_DIR, PARQUET_DIR):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    con = duckdb.connect(str(DB_PATH))
    all_tables = {**raw_tables, **clean_tables, **helper_tables}
    for name, df in all_tables.items():
        con.register("tmp_df", df)
        con.execute(f"CREATE TABLE {name} AS SELECT * FROM tmp_df")
        con.unregister("tmp_df")
    # tipe kolom dibuat eksplisit
    con.execute("ALTER TABLE orders ALTER order_date TYPE VARCHAR")
    for t in ("orders", "orders_clean"):
        con.execute(f"ALTER TABLE {t} ALTER updated_at TYPE TIMESTAMP")
    con.execute("ALTER TABLE order_items ALTER quantity TYPE INTEGER")
    con.execute("ALTER TABLE dim_product ALTER updated_at TYPE TIMESTAMP")
    con.execute("ALTER TABLE product_updates ALTER updated_at TYPE TIMESTAMP")
    con.execute("ALTER TABLE distributor_snapshot ALTER address TYPE VARCHAR")

    for name in all_tables:
        con.execute(f"COPY {name} TO '{(PARQUET_DIR / (name + '.parquet')).as_posix()}' (FORMAT PARQUET)")
    for name in raw_tables:
        con.execute(f"COPY {name} TO '{(RAW_DIR / (name + '.csv')).as_posix()}' (HEADER, DELIMITER ',')")
    con.execute("CHECKPOINT")

    print("Dataset dibuat:")
    for name in all_tables:
        n = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        print(f"  {name:<24}{n:>8,} baris")
    con.close()
    print(f"\nDuckDB : {DB_PATH}\nCSV    : {RAW_DIR}\nParquet: {PARQUET_DIR}")


if __name__ == "__main__":
    main()
