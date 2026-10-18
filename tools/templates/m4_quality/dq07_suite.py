"""
DQ07 | Suite pengecekan berbasis konfigurasi
Tingkat: SEDANG

SOAL
  Di pipeline nyata, aturan kualitas ditulis sebagai konfigurasi (YAML/JSON, seperti dbt
  atau Great Expectations), lalu satu runner menjalankan semuanya.

  1. run_suite(tables, rules) -> DataFrame laporan
       tables : dict nama_tabel -> DataFrame
       rules  : list dict. Setiap rule punya "table", "check", dan opsional "severity"
                ('error' default, atau 'warn'). Jenis check:
                  {"check": "not_null", "column": c}                     -> DQ01 (max_null_rate 0)
                  {"check": "unique", "columns": [..]}                    -> DQ02
                  {"check": "accepted_values", "column": c, "values": [..]} -> DQ03 (case sensitive)
                  {"check": "range", "column": c, "min": x, "max": y}    -> DQ03 (min/max opsional)
                  {"check": "relationship", "column": c, "to": tabel_parent, "field": kolom_parent}
                                                                          -> DQ04 (allow_null True)
                Panggil fungsi dari latihan sebelumnya dengan import biasa, misalnya
                    from dq01_completeness import check_completeness
       Kolom laporan (urut): table, check, severity, passed, failed_rows, total_rows
         check di laporan = CheckResult.check
       Urutan baris laporan = urutan rules.
       Jenis check tidak dikenal atau tabel tidak ada: raise ValueError.

  2. should_block(report) -> bool
       True kalau ada baris dengan passed False DAN severity 'error'. Pengecekan 'warn'
       yang gagal tidak memblokir pipeline.

Uji     : task test-quality -- -k dq07
Petunjuk: task hint -- dq07
"""

from __future__ import annotations

import pandas as pd


def run_suite(tables: dict[str, pd.DataFrame], rules: list[dict]) -> pd.DataFrame:
    raise NotImplementedError


def should_block(report: pd.DataFrame) -> bool:
    raise NotImplementedError
