"""
P01 | Extract: membaca CSV mentah dengan aman
Tingkat: MUDAH

SOAL
  Lengkapi extract_csv(path). Prinsip tahap extract: ambil data apa adanya dan jangan
  biarkan library menebak tipe data. Konversi tipe adalah tugas tahap transform.

  Aturan:
  1. Semua kolom dibaca sebagai string. Contoh: '007' tetap '007', '1.50' tetap '1.50',
     tanggal tidak boleh berubah jadi datetime.
  2. HANYA nilai berikut yang dianggap missing (NaN): '' (kosong), 'NA', 'N/A', 'null', 'NULL'.
     Nilai lain, misalnya 'None', tetap string apa adanya.
  3. Tambahkan kolom _source_file berisi NAMA file saja (contoh 'orders.csv'), bukan path lengkap.
  4. Kalau file tidak ada, raise FileNotFoundError yang pesannya menyebut path file tersebut.
  5. File yang hanya berisi header menghasilkan DataFrame kosong dengan kolom sesuai header
     ditambah _source_file.

Uji     : task test-python -- -k p01
Petunjuk: task hint -- p01
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

NULL_MARKERS = ["", "NA", "N/A", "null", "NULL"]


def extract_csv(path: str | Path) -> pd.DataFrame:
    raise NotImplementedError
