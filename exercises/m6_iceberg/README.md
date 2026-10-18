# Modul 6: Lakehouse dan Apache Iceberg (lokal)

Semua latihan memakai **PyIceberg** dengan **SQL catalog (SQLite)** dan warehouse di folder
lokal. Tidak ada server, tidak ada cloud. Baca dulu `METADATA_ICEBERG.md` (10 menit).

`ice_base.py` sudah jadi: `get_catalog(root)` membuat catalog SQLite + warehouse di folder
`root`. Helper ini sudah menangani masalah path Windows (lihat komentar di dalamnya).

| No | File | Topik |
|---|---|---|
| ICE01 | `ice01_create_table.py` | Namespace, schema dengan field id, partisi `day(order_ts)` |
| ICE02 | `ice02_append.py` | Pandas ke Arrow sesuai schema tabel, append, snapshot baru |
| ICE03 | `ice03_schema_evolution.py` | Tambah kolom tanpa menulis ulang data |
| ICE04 | `ice04_snapshots.py` | Membaca daftar snapshot dan summary-nya |
| ICE05 | `ice05_time_travel.py` | Baca per snapshot id, per waktu, dan diff antar snapshot |
| ICE06 | `ice06_partition_pruning.py` | Hidden partitioning: filter kolom asli, file yang dibaca berkurang |
| ICE07 | `ice07_metadata.py` | Membaca `metadata.json` langsung |

Uji: `task test-iceberg` (satu latihan: `task test-iceberg -- -k ice03`).
Petunjuk: `task hint -- ice03`.

Mau bereksperimen bebas? Jalankan `task iceberg-demo`. Perintah ini membuat tabel contoh dari
data warehouse di `exercises/m6_iceberg/playground/`, lalu mencetak isi folder metadata-nya.
