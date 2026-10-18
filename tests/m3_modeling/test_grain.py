"""Penilai latihan grain/fact/dimension (Modul 3)."""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
KEY = yaml.safe_load((ROOT / "solutions" / "m3_modeling" / "grain_fact_dim.yaml").read_text(encoding="utf-8"))
IDS = sorted(KEY)

FACT_TYPES = {"transaction", "periodic_snapshot", "accumulating_snapshot", "factless"}
ADDITIVITY = {"additive", "semi_additive", "non_additive"}
DIMENSIONS = {"tanggal", "bulan", "produk", "kategori_produk", "batch", "distributor", "region",
              "sales_rep", "gudang", "outlet_apotek", "promosi", "alasan_retur"}


@pytest.fixture(scope="module")
def answers(answers_root):
    path = answers_root / "m3_modeling" / "grain_fact_dim.yaml"
    if not path.exists():
        pytest.fail(f"File jawaban tidak ditemukan: {path}", pytrace=False)
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        pytest.fail(f"grain_fact_dim.yaml tidak valid sebagai YAML (cek indentasi):\n{e}", pytrace=False)


def _norm(v):
    return str(v).strip().lower() if v is not None else None


def _check(gid, ans, key) -> list[str]:
    msgs = []
    if "scd" in key:
        got = ans.get("scd") or {}
        for attr, exp in key["scd"].items():
            v = got.get(attr)
            if v is None:
                msgs.append(f"scd.{attr} belum diisi.")
            elif str(v).strip() not in {"0", "1", "2", "3"}:
                msgs.append(f"scd.{attr} harus 0, 1, 2, atau 3 (diisi {v!r}).")
            elif int(v) != exp:
                msgs.append(f"Tipe SCD untuk {attr} belum tepat. Baca lagi kebutuhan histori atribut ini.")
        return msgs

    grain = _norm(ans.get("grain"))
    if grain is None:
        msgs.append("grain belum diisi.")
    elif grain not in {"a", "b", "c", "d"}:
        msgs.append(f"grain harus a, b, c, atau d (diisi {ans.get('grain')!r}).")
    elif grain != key["grain"]:
        msgs.append("grain belum tepat. Tanyakan: SATU baris di tabel ini mewakili apa, dan apakah "
                    "grain ini cukup detail untuk semua pertanyaan di skenario?")

    ft = _norm(ans.get("fact_type"))
    accepted = key.get("fact_type_diterima", [key["fact_type"]])
    if ft is None:
        msgs.append("fact_type belum diisi.")
    elif ft not in FACT_TYPES:
        msgs.append(f"fact_type harus salah satu dari {sorted(FACT_TYPES)} (diisi {ans.get('fact_type')!r}).")
    elif ft not in accepted:
        msgs.append("fact_type belum tepat. Apakah baris dicatat per kejadian, per periode tetap, "
                    "diperbarui mengikuti proses, atau tanpa angka sama sekali?")

    got_m = ans.get("measures") or {}
    for m, exp in key["measures"].items():
        v = _norm(got_m.get(m))
        if v is None:
            msgs.append(f"additivity measure '{m}' belum diisi.")
        elif v not in ADDITIVITY:
            msgs.append(f"measure '{m}' harus {sorted(ADDITIVITY)} (diisi {got_m.get(m)!r}).")
        elif v != exp:
            msgs.append(f"additivity measure '{m}' belum tepat. Coba jumlahkan nilainya antar hari "
                        "dan antar produk/distributor: apakah hasilnya bermakna?")
    extra_m = set(got_m) - set(key["measures"])
    if extra_m:
        msgs.append(f"Jangan menambah atau mengganti nama measure: {sorted(extra_m)}.")

    dims = {_norm(d) for d in (ans.get("dimensions") or [])}
    unknown = dims - DIMENSIONS
    if unknown:
        msgs.append(f"Nama dimensi tidak dikenal: {sorted(unknown)}. Pilih dari daftar di header file.")
    if not dims:
        msgs.append("dimensions belum diisi.")
    else:
        miss = set(key["dims_wajib"]) - dims
        bad = dims & set(key["dims_dilarang"])
        if miss:
            msgs.append(f"Ada {len(miss)} dimensi wajib yang belum dipilih.")
        if bad:
            msgs.append(f"Ada {len(bad)} dimensi yang levelnya tidak cocok dengan grain.")
    return msgs


@pytest.mark.parametrize("gid", IDS)
def test_grain(gid, answers, record_property):
    record_property("exercise", f"m3_modeling/{gid}")
    ans = answers.get(gid)
    if not isinstance(ans, dict):
        pytest.fail(f"{gid} tidak ditemukan di grain_fact_dim.yaml.", pytrace=False)
    msgs = _check(gid, ans, KEY[gid])
    if msgs:
        pytest.fail(f"{gid.upper()} belum benar:\n" + "\n".join(f"- {m}" for m in msgs)
                    + f"\n\nButuh petunjuk? task hint -- {gid}", pytrace=False)
