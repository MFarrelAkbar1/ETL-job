"""Fixture Modul 6."""

import pytest

from py_loader import load

MODULE = "m6_iceberg"


@pytest.fixture(autouse=True)
def _record_exercise(request, record_property):
    ex = getattr(request.module, "EX", None)
    if ex:
        record_property("exercise", f"{MODULE}/{ex}")


@pytest.fixture
def ex(request, answers_root):
    return load(answers_root, request.module.FILE, MODULE)
