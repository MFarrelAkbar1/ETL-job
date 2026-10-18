"""Memuat file jawaban Python (Modul 2, 4, 6, ...) dan mengubah NotImplementedError jadi pesan yang jelas."""

from __future__ import annotations

import contextlib
import functools
import importlib.util
import inspect
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _purge():
    for k in [k for k in sys.modules if re.match(r"^(p\d\d_|dq\d\d_|dq_base$|ice\d\d_)", k)]:
        del sys.modules[k]


@contextlib.contextmanager
def on_path(folder: Path):
    sys.path.insert(0, str(folder))
    try:
        yield
    finally:
        with contextlib.suppress(ValueError):
            sys.path.remove(str(folder))


class _Proxy:
    def __init__(self, mod, folder: Path):
        self._mod, self._folder = mod, folder

    def __getattr__(self, name):
        if not hasattr(self._mod, name):
            pytest.fail(f"Fungsi/kelas '{name}' tidak ditemukan di {Path(self._mod.__file__).name}. "
                        "Jangan ganti nama fungsi yang sudah disediakan.", pytrace=False)
        obj = getattr(self._mod, name)
        if inspect.isfunction(obj):
            @functools.wraps(obj)
            def wrapper(*a, **kw):
                with on_path(self._folder):
                    try:
                        return obj(*a, **kw)
                    except NotImplementedError:
                        pass
                # pytest.fail di luar blok except supaya traceback tidak berantai
                pytest.fail(f"Belum dikerjakan: {name}() di {Path(self._mod.__file__).name} "
                            "masih raise NotImplementedError.", pytrace=False)
            return wrapper
        return obj


def load(root: Path, name: str, module: str = "m2_python") -> _Proxy:
    folder = root / module
    path = folder / f"{name}.py"
    if not path.exists():
        pytest.fail(f"File jawaban tidak ditemukan: {path}", pytrace=False)
    _purge()
    with on_path(folder):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception as e:  # noqa: BLE001
            pytest.fail(f"{path.name} gagal di-import: {type(e).__name__}: {e}", pytrace=False)
    return _Proxy(mod, folder)
