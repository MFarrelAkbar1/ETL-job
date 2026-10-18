"""Konfigurasi pytest bersama.

Opsi:
  --answers=exercises   (default) menilai file jawaban Anda di exercises/
  --answers=solutions   menilai kunci jawaban (dipakai untuk verifikasi soal)
  --answers=<folder>    menilai folder lain dengan struktur sama (dipakai mode timed)
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
PROGRESS_FILE = ROOT / ".progress" / "results.json"
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools"))

_results: dict[str, dict] = {}


def pytest_addoption(parser):
    parser.addoption("--answers", action="store", default="exercises",
                     help="exercises | solutions | path folder jawaban")


@pytest.fixture(scope="session")
def answers_root(request) -> Path:
    val = request.config.getoption("--answers")
    p = Path(val)
    if not p.is_absolute():
        p = ROOT / p
    if not p.exists():
        pytest.exit(f"Folder jawaban tidak ditemukan: {p}", returncode=2)
    return p


def _is_default_answers(config) -> bool:
    return config.getoption("--answers") == "exercises"


def pytest_runtest_logreport(report):
    ex = dict(report.user_properties).get("exercise")
    if not ex:
        return
    if report.when == "call" or (report.when == "setup" and report.failed):
        prev = _results.get(ex)
        passed = report.passed and (prev is None or prev["passed"])
        _results[ex] = {"passed": passed, "ts": time.strftime("%Y-%m-%d %H:%M:%S")}


def pytest_sessionfinish(session, exitstatus):
    if not _results or not _is_default_answers(session.config):
        return
    PROGRESS_FILE.parent.mkdir(exist_ok=True)
    data = {}
    if PROGRESS_FILE.exists():
        try:
            data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
    data.update(_results)
    PROGRESS_FILE.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
