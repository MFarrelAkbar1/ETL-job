"""Mode timed: meniru live test SQL.

  task timed                          5 soal acak, 15 menit
  task timed -- --n 3 --minutes 10    atur sendiri
  task timed -- --priority            hanya dari 10 soal prioritas

File soal dibuat di exercises/timed/<waktu>/m1_sql/. Kerjakan di editor, lalu tekan
ENTER di terminal kalau sudah selesai. Kalau waktu habis, penilaian berjalan otomatis.
"""

from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
import threading
import time
from pathlib import Path

from render_exercises import render
from sql_questions import QUESTIONS

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / ".progress" / "timed.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--minutes", type=float, default=15)
    ap.add_argument("--priority", action="store_true")
    ap.add_argument("--seed", type=int)
    args = ap.parse_args()

    pool = [q for q in QUESTIONS if q["priority"]] if args.priority else QUESTIONS
    rnd = random.Random(args.seed)
    picked = sorted(rnd.sample(pool, k=min(args.n, len(pool))), key=lambda q: q["id"])

    stamp = time.strftime("%Y%m%d-%H%M%S")
    folder = ROOT / "exercises" / "timed" / stamp
    (folder / "m1_sql").mkdir(parents=True)
    for q in picked:
        (folder / "m1_sql" / f"{q['id']}.sql").write_text(render(q), encoding="utf-8", newline="\n")

    total_s = int(args.minutes * 60)
    print("=" * 64)
    print(f" MODE TIMED: {len(picked)} soal, {args.minutes:g} menit")
    print("=" * 64)
    for q in picked:
        print(f"  {q['id'].upper()}  [{q['level']:<6}] {q['title']}")
    print(f"\nFile soal: {folder / 'm1_sql'}")
    print("Buka di editor dan kerjakan. Tekan ENTER di sini kalau sudah selesai.\n")

    done = threading.Event()

    def wait_enter():
        try:
            input()
        except EOFError:
            pass
        done.set()

    threading.Thread(target=wait_enter, daemon=True).start()
    start = time.time()
    announced = set()
    while not done.is_set():
        left = total_s - int(time.time() - start)
        if left <= 0:
            print("\nWAKTU HABIS. Menilai jawaban...")
            break
        # umumkan tiap menit penuh, lalu tiap 10 detik di menit terakhir
        mark = left // 60 if left > 60 else -(left // 10)
        if mark not in announced:
            announced.add(mark)
            print(f"  Sisa waktu: {left // 60} menit {left % 60:02d} detik", flush=True)
        done.wait(1)
    elapsed = time.time() - start

    ids = [q["id"] for q in picked]
    cmd = [sys.executable, "-m", "pytest", "tests/m1_sql", f"--answers={folder}", "-k", " or ".join(ids)]
    print("\n")
    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    print(res.stdout[-6000:])
    passed = _count_passed(res.stdout)
    print("=" * 64)
    print(f" Hasil: {passed} dari {len(ids)} soal benar, waktu {elapsed / 60:.1f} menit")
    print("=" * 64)

    HISTORY.parent.mkdir(exist_ok=True)
    hist = json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else []
    hist.append(dict(at=stamp, ids=ids, passed=passed, total=len(ids), minutes=round(elapsed / 60, 1)))
    HISTORY.write_text(json.dumps(hist, indent=2), encoding="utf-8")


def _count_passed(out: str) -> int:
    import re
    m = re.search(r"(\d+) passed", out)
    return int(m.group(1)) if m else 0


if __name__ == "__main__":
    main()
