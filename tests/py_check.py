"""Helper assertion dengan pesan Bahasa Indonesia tanpa traceback panjang."""

import pytest


def check(cond, msg: str):
    if not cond:
        pytest.fail(msg, pytrace=False)


def expect_raises(exc_type, func, *args, msg: str, **kwargs):
    try:
        func(*args, **kwargs)
    except exc_type as e:
        return e
    except Exception as e:  # noqa: BLE001
        pytest.fail(f"{msg}\n  Yang terjadi: raise {type(e).__name__}: {e}", pytrace=False)
    pytest.fail(f"{msg}\n  Yang terjadi: tidak ada exception sama sekali.", pytrace=False)
