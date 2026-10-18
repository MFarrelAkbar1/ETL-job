"""Fixture Modul 2."""

import pytest

from py_loader import ROOT, load


@pytest.fixture(autouse=True)
def _record_exercise(request, record_property):
    ex = getattr(request.module, "EX", None)
    if ex:
        record_property("exercise", f"m2_python/{ex}")


@pytest.fixture
def ex(request, answers_root):
    """Modul jawaban untuk file test ini (ditentukan oleh konstanta FILE di file test)."""
    return load(answers_root, request.module.FILE)


@pytest.fixture
def sol():
    return lambda name: load(ROOT / "solutions", name)
