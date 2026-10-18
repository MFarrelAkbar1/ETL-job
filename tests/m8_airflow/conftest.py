"""Fixture Modul 8."""

from pathlib import Path

import pytest

from dag_ast import analyze

MODULE = "m8_airflow"


@pytest.fixture(autouse=True)
def _record_exercise(request, record_property):
    ex = getattr(request.module, "EX", None)
    if ex:
        record_property("exercise", f"{MODULE}/{ex}")


@pytest.fixture
def dag(request, answers_root):
    path = Path(answers_root) / MODULE / f"{request.module.FILE}.py"
    if not path.exists():
        pytest.fail(f"File jawaban tidak ditemukan: {path}", pytrace=False)
    info = analyze(path)
    if info.n_dags == 0 and not info.tasks:
        pytest.fail(f"Belum dikerjakan: belum ada DAG di {path.name}.", pytrace=False)
    if info.problems:
        pytest.fail(f"{path.name} belum bisa dianalisis:\n- " + "\n- ".join(info.problems), pytrace=False)
    if info.n_dags != 1:
        pytest.fail(f"{path.name} harus berisi tepat satu DAG, ditemukan {info.n_dags}.", pytrace=False)
    return info
