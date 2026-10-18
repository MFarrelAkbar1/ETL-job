"""Menampilkan progres per modul berdasarkan hasil test terakhir.

Hasil dicatat otomatis setiap kali Anda menjalankan test (task test-sql, test-python, dst).
  task progress            ringkasan
  task progress -- --all   tampilkan juga status per soal
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from registry import MODULES

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / ".progress" / "results.json"
TIMED = ROOT / ".progress" / "timed.json"
CASES_DIR = ROOT / "exercises" / "m3_modeling"


def bar(done: int, total: int, width: int = 25) -> str:
    filled = int(width * done / total) if total else 0
    return "[" + "#" * filled + "." * (width - filled) + "]"


def case_status() -> list[tuple[str, int]]:
    out = []
    for f in sorted(CASES_DIR.glob("kasus_*.md")):
        text = f.read_text(encoding="utf-8")
        parts = text.split("## Jawaban Saya", 1)
        ans = parts[1] if len(parts) > 1 else ""
        ans = re.sub(r"<!--.*?-->", "", ans, flags=re.S)
        words = len(re.findall(r"\w+", ans))
        out.append((f.stem, words))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    res = json.loads(RESULTS.read_text(encoding="utf-8")) if RESULTS.exists() else {}

    print("=" * 66)
    print(" PROGRES BELAJAR")
    print("=" * 66)
    grand_done = grand_total = 0
    for mod, info in MODULES.items():
        ids = info["ids"]
        status = {i: res.get(f"{mod}/{i}") for i in ids}
        done = sum(1 for s in status.values() if s and s["passed"])
        grand_done += done
        grand_total += len(ids)
        print(f"\n{info['title']}")
        print(f"  {bar(done, len(ids))} {done}/{len(ids)} lulus")
        if info["priority"]:
            pd_ = sum(1 for i in info["priority"] if status[i] and status[i]["passed"])
            print(f"  Prioritas interview: {pd_}/{len(info['priority'])} lulus")
        failing = [i for i, s in status.items() if s and not s["passed"]]
        untested = [i for i, s in status.items() if not s]
        if failing:
            print(f"  Belum lulus : {', '.join(failing)}")
        if untested and args.all:
            print(f"  Belum diuji : {', '.join(untested)}")
        if args.all:
            for i, s in status.items():
                mark = "LULUS" if s and s["passed"] else ("gagal" if s else "-")
                star = " *" if i in info["priority"] else ""
                print(f"    {i}{star:<3} {mark:<6} {s['ts'] if s else ''}")

    cases = case_status()
    if cases:
        answered = sum(1 for _, w in cases if w >= 80)
        print("\nModul 3: Studi kasus (dinilai mandiri dengan rubrik)")
        print(f"  {bar(answered, len(cases))} {answered}/{len(cases)} sudah dijawab (minimal 80 kata)")
        for name, w in cases:
            print(f"    {name:<12} {w:>4} kata")

    if TIMED.exists():
        hist = json.loads(TIMED.read_text(encoding="utf-8"))[-5:]
        print("\nMode timed (5 terakhir)")
        for h in hist:
            print(f"    {h['at']}  {h['passed']}/{h['total']} benar  {h['minutes']} menit")

    print("\n" + "-" * 66)
    print(f" Total soal otomatis: {grand_done}/{grand_total} lulus")
    print("-" * 66)


if __name__ == "__main__":
    main()
