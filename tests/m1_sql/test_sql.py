"""Penilai Modul 1 (SQL).

Jalankan satu soal:  task test-sql -- -k s07
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sql_grader import (ROOT, diagnose, execute, frames_match, open_readonly, open_sandbox,
                        read_answer, static_violations, strip_comments)
from sql_questions import QUESTIONS

from sql_spec import SPECS

SOLUTIONS = ROOT / "solutions" / "m1_sql"
IDS = [q["id"] for q in QUESTIONS]
_expected_cache: dict = {}


@pytest.fixture(scope="module")
def ro_con():
    con = open_readonly()
    yield con
    con.close()


def _solution_sql(sid: str) -> str:
    return strip_comments((SOLUTIONS / f"{sid}.sql").read_text(encoding="utf-8"))


def _fail(sid: str, msgs: list[str]):
    body = "\n".join(f"- {m}" for m in msgs)
    pytest.fail(f"{sid.upper()} belum benar:\n{body}\n\nButuh petunjuk? task hint -- {sid}", pytrace=False)


def _check_select(sid, spec, user_sql, con):
    if sid not in _expected_cache:
        _expected_cache[sid] = execute(con, _solution_sql(sid), who="kunci jawaban")
    expected = _expected_cache[sid]
    user = execute(con, user_sql)
    if user is None:
        pytest.fail(f"{sid.upper()}: statement terakhir di file harus berupa SELECT yang mengembalikan hasil.",
                    pytrace=False)
    msgs = []
    ordered = spec.get("ordered", False)
    if not frames_match(user, expected, ordered):
        for hint, wrong_sql in spec.get("mistakes", []):
            wrong = execute(con, wrong_sql, who="pembanding")
            if wrong is not None and frames_match(user, wrong, ordered=False):
                msgs.append("Diagnosis: " + hint)
        msgs += diagnose(user, expected, ordered)
        if not msgs:
            msgs.append("Hasil belum sama dengan jawaban benar.")
    if spec.get("static"):
        msgs += static_violations(user_sql, spec["static"])
    if msgs:
        _fail(sid, msgs)


def _dml_state(spec, sql, who, runs=1):
    con = open_sandbox(spec["tables"])
    states = []
    for _ in range(runs):
        execute(con, sql, who=who)
        cols = [r[0] for r in con.execute(f"DESCRIBE {spec['check_table']}").fetchall()]
        keep = [c for c in cols if c not in spec.get("exclude_cols", [])]
        df = con.execute(f"SELECT {', '.join(keep)} FROM {spec['check_table']} "
                         f"ORDER BY {spec['order_by']}").df()
        states.append(df)
    uc = spec.get("unique_col")
    uniq_problem = None
    if uc:
        n_null, n_dup = con.execute(
            f"SELECT COUNT(*) FILTER (WHERE {uc} IS NULL), COUNT({uc}) - COUNT(DISTINCT {uc}) "
            f"FROM {spec['check_table']}").fetchone()
        if n_null or n_dup:
            uniq_problem = f"Kolom {uc} punya {n_null} NULL dan {n_dup} duplikat. Surrogate key harus unik."
    con.close()
    return states, uniq_problem


def _check_dml(sid, spec, user_sql):
    if sid not in _expected_cache:
        _expected_cache[sid] = _dml_state(spec, _solution_sql(sid), "kunci jawaban")[0][0]
    expected = _expected_cache[sid]
    runs = 2 if spec.get("idempotent") else 1
    states, uniq_problem = _dml_state(spec, user_sql, "Anda", runs=runs)
    msgs = []
    first = states[0]
    if not frames_match(first, expected, ordered=True):
        msgs.append(f"Isi akhir tabel {spec['check_table']} (diurutkan {spec['order_by']}) belum sesuai.")
        msgs += diagnose(first, expected, ordered=True)
    elif runs == 2 and not frames_match(states[1], first, ordered=True):
        msgs.append("Jalan pertama sudah benar, tapi hasilnya BERUBAH saat statement dijalankan kedua kali. "
                    "Pipeline yang di-retry harus idempotent.")
        msgs += diagnose(states[1], first, ordered=True)
    if uniq_problem:
        msgs.append(uniq_problem)
    if msgs:
        _fail(sid, msgs)


@pytest.mark.parametrize("sid", IDS)
def test_sql(sid, answers_root: Path, record_property, ro_con):
    record_property("exercise", f"m1_sql/{sid}")
    spec = SPECS.get(sid, {})
    user_sql = read_answer(answers_root / "m1_sql" / f"{sid}.sql")
    if spec.get("kind") == "dml":
        _check_dml(sid, spec, user_sql)
    else:
        _check_select(sid, spec, user_sql, ro_con)
