"""Kembalikan file latihan ke kondisi kosong (jawaban Anda akan HILANG).

  task reset -- s07      satu soal SQL
  task reset -- p03      satu latihan Python
  task reset -- g        file grain_fact_dim.yaml
  task reset -- k02      satu studi kasus
  task reset -- dq03     satu latihan data quality
  task reset -- ice03    satu latihan Iceberg
  task reset -- dag02    satu latihan Airflow
  task reset -- all      semua (diminta konfirmasi)
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

from sql_questions import BY_ID

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "tools" / "templates"
EX = ROOT / "exercises"


def _restore(rel: str):
    src, dst = TEMPLATES / rel, EX / rel
    shutil.copyfile(src, dst)
    print(f"Dikosongkan: exercises/{rel}")


def _reset_sql(sid: str):
    from render_exercises import OUT, render
    (OUT / f"{sid}.sql").write_text(render(BY_ID[sid]), encoding="utf-8", newline="\n")
    print(f"Dikosongkan: exercises/m1_sql/{sid}.sql")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--yes", action="store_true")
    a = ap.parse_args()
    t = a.target.lower()

    if t == "all":
        if not a.yes:
            ans = input("SEMUA jawaban Anda di exercises/ akan dihapus. Ketik 'ya' untuk lanjut: ")
            if ans.strip().lower() != "ya":
                print("Dibatalkan.")
                return
        for sid in BY_ID:
            _reset_sql(sid)
        for f in sorted(TEMPLATES.rglob("*")):
            if f.is_file():
                _restore(f.relative_to(TEMPLATES).as_posix())
        return
    if t in BY_ID:
        _reset_sql(t)
    elif re.fullmatch(r"p\d\d", t):
        matches = list((TEMPLATES / "m2_python").glob(f"{t}_*.py"))
        if not matches:
            sys.exit(f"Latihan {t} tidak ditemukan.")
        _restore(f"m2_python/{matches[0].name}")
    elif re.fullmatch(r"dq0[1-8]", t):
        matches = list((TEMPLATES / "m4_quality").glob(f"{t}_*.py"))
        _restore(f"m4_quality/{matches[0].name}")
    elif re.fullmatch(r"ice0[1-7]", t):
        matches = list((TEMPLATES / "m6_iceberg").glob(f"{t}_*.py"))
        _restore(f"m6_iceberg/{matches[0].name}")
    elif re.fullmatch(r"dag0[1-3]", t):
        matches = list((TEMPLATES / "m8_airflow").glob(f"{t}_*.py"))
        _restore(f"m8_airflow/{matches[0].name}")
    elif t in ("g", "grain"):
        _restore("m3_modeling/grain_fact_dim.yaml")
    elif re.fullmatch(r"k0[1-5]", t):
        _restore(f"m3_modeling/kasus_{t[1:]}.md")
    else:
        sys.exit(f"Target '{a.target}' tidak dikenal. Contoh: s07, p03, g, k02, dq03, ice03, dag02, all")


if __name__ == "__main__":
    main()
