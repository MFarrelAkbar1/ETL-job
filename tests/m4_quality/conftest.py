"""Fixture Modul 4."""

import pytest

from py_loader import ROOT, load

MODULE = "m4_quality"


@pytest.fixture(autouse=True)
def _record_exercise(request, record_property):
    ex = getattr(request.module, "EX", None)
    if ex:
        record_property("exercise", f"{MODULE}/{ex}")


@pytest.fixture
def ex(request, answers_root):
    return load(answers_root, request.module.FILE, MODULE)


@pytest.fixture
def sol():
    return lambda name: load(ROOT / "solutions", name, MODULE)
