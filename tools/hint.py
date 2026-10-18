"""Petunjuk bertahap, 3 level, tanpa jawaban penuh.

  task hint -- s07          buka level berikutnya untuk soal s07
  task hint -- s07 --reset  mulai lagi dari level 1
  task hint -- list         lihat soal yang punya petunjuk
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".progress" / "hints.json"


def load_hints() -> dict[str, list[str]]:
    hints: dict[str, list[str]] = {}
    for f in sorted((ROOT / "hints").glob("*.yaml")):
        hints.update(yaml.safe_load(f.read_text(encoding="utf-8")) or {})
    return hints


def main():
    ap = argparse.ArgumentParser(description="Petunjuk bertahap")
    ap.add_argument("id", nargs="?", help="nomor soal, mis. s07, p03, g02, k01")
    ap.add_argument("--reset", action="store_true")
    args = ap.parse_args()

    hints = load_hints()
    if not args.id or args.id == "list":
        print("Soal dengan petunjuk:", ", ".join(sorted(hints)))
        print("Pemakaian: task hint -- s07")
        return
    sid = args.id.lower().strip()
    if sid not in hints:
        print(f"Tidak ada petunjuk untuk '{sid}'. Ketik: task hint -- list")
        sys.exit(1)

    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    if args.reset:
        state.pop(sid, None)
        print(f"Petunjuk {sid} di-reset ke level 0.")
    else:
        level = min(state.get(sid, 0) + 1, len(hints[sid]))
        state[sid] = level
        print(f"Petunjuk {sid.upper()} (level {level} dari {len(hints[sid])})")
        print("-" * 60)
        for i, h in enumerate(hints[sid][:level], start=1):
            print(f"[{i}] {h}")
        if level == len(hints[sid]):
            print("\nIni level terakhir. Kalau masih buntu, bandingkan dengan solutions/ SETELAH mencoba.")
        else:
            print(f"\nJalankan lagi untuk membuka level {level + 1}.")
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
