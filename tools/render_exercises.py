"""Membuat file soal SQL kosong dari bank soal.

  python tools/render_exercises.py              buat file yang belum ada (tidak menimpa jawaban)
  python tools/render_exercises.py --reset s07  kosongkan ulang satu soal
  python tools/render_exercises.py --reset all  kosongkan ulang semua soal SQL
"""

from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

from sql_questions import QUESTIONS, REVENUE_RULE

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "exercises" / "m1_sql"
ANSWER_MARK = "-- Tulis jawaban Anda DI BAWAH baris ini"


def level_label(q: dict) -> str:
    return q["level"].upper()


def render(q: dict, timed: bool = False) -> str:
    bar = "-- " + "=" * 74
    prio = "YA (sering muncul di interview)" if q["priority"] else "-"
    body = "\n".join("--   " + line if line else "--" for line in q["question"].splitlines())
    lines = [
        bar,
        f"-- {q['id'].upper()} | {q['title']}",
        f"-- Tingkat: {level_label(q)} | Prioritas: {prio}",
        bar,
        "-- SOAL",
        body,
        "--",
        f"-- Tabel        : {q['tables']}",
    ]
    if q.get("kind") != "dml":
        lines += [
            f"-- Kolom output : {q['columns']}",
            f"-- Urutan baris : {q['order']}",
        ]
    lines += [
        "--",
        "-- " + "\n-- ".join(textwrap.wrap(REVENUE_RULE, 74)),
        "--",
        f"-- Uji jawaban  : task test-sql -- -k {q['id']}",
        f"-- Petunjuk     : task hint -- {q['id']}   (3 level, dibuka bertahap)",
        bar,
        "",
        ANSWER_MARK,
        "",
        "",
    ]
    return "\n".join(lines)


def render_index() -> str:
    rows = ["# Modul 1: SQL (25 soal)", "",
            "Kerjakan berurutan. Kalau waktu terbatas, dahulukan soal berlabel **PRIORITAS**.", "",
            "| No | Judul | Tingkat | Prioritas |", "|---|---|---|---|"]
    for q in QUESTIONS:
        rows.append(f"| {q['id'].upper()} | {q['title']} | {q['level']} | {'**PRIORITAS**' if q['priority'] else ''} |")
    prio = ", ".join(q["id"].upper() for q in QUESTIONS if q["priority"])
    rows += ["", f"Urutan kilat 10 soal prioritas: {prio}.", "",
             "Kamus data dan definisi bisnis: `data/KAMUS_DATA.md`.", ""]
    return "\n".join(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", help="id soal (mis. s07) atau 'all'")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    targets = set()
    if args.reset:
        targets = {q["id"] for q in QUESTIONS} if args.reset == "all" else {args.reset.lower()}
    n = 0
    for q in QUESTIONS:
        p = OUT / f"{q['id']}.sql"
        if p.exists() and q["id"] not in targets:
            continue
        p.write_text(render(q), encoding="utf-8", newline="\n")
        n += 1
    (OUT / "INDEX.md").write_text(render_index(), encoding="utf-8", newline="\n")
    print(f"{n} file soal SQL dibuat/dikosongkan di {OUT}")


if __name__ == "__main__":
    main()
