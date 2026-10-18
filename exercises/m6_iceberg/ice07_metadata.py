"""
ICE07 | Membaca metadata.json langsung
Tingkat: SEDANG

SOAL
  metadata_summary(table) -> dict

  Buka file metadata TERKINI (table.metadata_location, path lokal) dengan modul json, lalu
  kembalikan dict:
    "format_version"        int
    "current_snapshot_id"   int atau None
    "n_snapshots"           jumlah snapshot di metadata
    "n_schemas"             jumlah versi schema yang tersimpan
    "current_schema_id"     int
    "n_previous_metadata"   jumlah entri metadata-log (versi metadata sebelumnya)
    "partition_fields"      list tuple (nama, transform, nama_kolom_sumber) dari spec default,
                            contoh [("order_day", "day", "order_ts")]. Nama kolom sumber
                            dicari dari field id di schema terkini.
    "manifest_list_exists"  bool, apakah file manifest list snapshot terkini benar-benar ada
                            di disk (False kalau tidak ada snapshot)

  Tujuan latihan ini adalah memahami isi metadata.json. Jangan memakai table.metadata;
  baca file JSON-nya.

Uji     : task test-iceberg -- -k ice07
Petunjuk: task hint -- ice07
"""

from __future__ import annotations

import json
from pathlib import Path

from pyiceberg.table import Table


def metadata_summary(table: Table) -> dict:
    raise NotImplementedError
