"""Kunci jawaban P10."""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path
from typing import Any, Callable

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


class TransientError(Exception):
    """Error sementara (timeout, koneksi putus) yang layak di-retry."""


def setup_logger(name: str, log_file: str | Path, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if getattr(logger, "_etl_configured", False):
        return logger  # sudah dikonfigurasi, jangan tambah handler lagi
    fmt = logging.Formatter(LOG_FORMAT)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    ch = logging.StreamHandler(sys.stderr)
    ch.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger._etl_configured = True
    return logger


def run_with_retry(func: Callable[[], Any], retries: int = 3, backoff_s: float = 0.0,
                   logger: logging.Logger | None = None) -> Any:
    log = logger or logging.getLogger(__name__)
    total = retries + 1
    for i in range(1, total + 1):
        try:
            result = func()
            log.info("berhasil pada percobaan %d/%d", i, total)
            return result
        except TransientError as e:
            if i == total:
                log.error("gagal setelah %d percobaan: %s", total, e)
                raise
            log.warning("percobaan %d/%d gagal: %s", i, total, e)
            time.sleep(backoff_s * 2 ** (i - 1))
        except Exception as e:
            log.error("error non-transient, tidak di-retry: %s", e)
            raise
