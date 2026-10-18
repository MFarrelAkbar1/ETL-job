"""
P10 | Logging dan error handling: retry yang benar
Tingkat: SEDANG

SOAL
  1. setup_logger(name, log_file, level=logging.INFO) -> logging.Logger
       - format: '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
       - menulis ke log_file DAN ke console (stderr)
       - dipanggil dua kali dengan nama yang sama TIDAK boleh menambah handler ganda
         (gejala klasik: setiap baris log muncul dua kali)

  2. run_with_retry(func, retries=3, backoff_s=0.0, logger=None)
       Jalankan func() tanpa argumen. Total percobaan maksimal = 1 + retries.
       - sukses           : log INFO, kembalikan hasil func
       - TransientError   : log WARNING berisi teks 'percobaan {i}/{total}' (contoh
                            'percobaan 1/4'), tunggu backoff_s * 2 ** (i - 1) detik, coba lagi
       - percobaan habis  : log ERROR, raise ulang exception TERAKHIR (jangan dibungkus)
       - exception lain   : JANGAN retry. Log ERROR lalu raise ulang exception tersebut
       Kalau logger None, pakai logging.getLogger(__name__).

Uji     : task test-python -- -k p10
Petunjuk: task hint -- p10
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Callable

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


class TransientError(Exception):
    """Error sementara (timeout, koneksi putus) yang layak di-retry."""


def setup_logger(name: str, log_file: str | Path, level: int = logging.INFO) -> logging.Logger:
    raise NotImplementedError


def run_with_retry(func: Callable[[], Any], retries: int = 3, backoff_s: float = 0.0,
                   logger: logging.Logger | None = None) -> Any:
    raise NotImplementedError
