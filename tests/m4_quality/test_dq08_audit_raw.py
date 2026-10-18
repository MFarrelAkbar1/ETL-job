from pathlib import Path

import pytest

from py_check import check
from py_loader import ROOT, load

EX, FILE = "dq08", "dq08_audit_raw"
RAW = ROOT / "data" / "raw"


@pytest.fixture(scope="module")
def expected():
    return load(ROOT / "solutions", FILE, "m4_quality").audit_raw(RAW)


def test_audit(ex, expected):
    rep = ex.audit_raw(RAW)
    check(list(rep.columns) == list(expected.columns), f"Kolom laporan harus {list(expected.columns)}.")
    check(len(rep) == len(expected), f"Laporan harus {len(expected)} baris (satu per rule), didapat {len(rep)}.")
    msgs = []
    for i, (u, e) in enumerate(zip(rep.itertuples(index=False), expected.itertuples(index=False))):
        if tuple(u) != tuple(e):
            hint = ""
            if u.check != e.check:
                hint = f"nama check {u.check!r}, seharusnya {e.check!r}"
            elif u.total_rows != e.total_rows:
                hint = f"total_rows {u.total_rows:,} (seharusnya {e.total_rows:,}): cek cara membaca CSV dan NULL"
            elif u.failed_rows != e.failed_rows:
                arah = "terlalu banyak" if u.failed_rows > e.failed_rows else "terlalu sedikit"
                hint = f"failed_rows {u.failed_rows:,} {arah}"
            else:
                hint = "passed/severity berbeda"
            msgs.append(f"rule ke-{i + 1} ({e.table}, {e.check}): {hint}")
    check(not msgs, "Laporan audit belum sesuai:\n  " + "\n  ".join(msgs)
          + "\n\nPetunjuk umum: baca CSV sebagai string dan hanya sel kosong yang NULL.")
