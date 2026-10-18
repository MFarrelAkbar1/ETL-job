# Modul 4: Data quality

8 latihan menulis pengecekan kualitas data dalam Python (pandas). Setiap pengecekan
mengembalikan `CheckResult` (lihat `dq_base.py`, sudah jadi, tidak perlu diubah).

| No | File | Dimensi kualitas |
|---|---|---|
| DQ01 | `dq01_completeness.py` | Completeness (NULL dan string kosong) |
| DQ02 | `dq02_uniqueness.py` | Uniqueness (primary key / natural key) |
| DQ03 | `dq03_validity.py` | Validity (rentang, nilai yang diizinkan, pola regex) |
| DQ04 | `dq04_referential.py` | Referential integrity (foreign key yatim) |
| DQ05 | `dq05_freshness.py` | Freshness dan volume anomali |
| DQ06 | `dq06_reconciliation.py` | Rekonsiliasi sumber vs target |
| DQ07 | `dq07_suite.py` | Suite berbasis konfigurasi + keputusan blokir pipeline |
| DQ08 | `dq08_audit_raw.py` | Audit data mentah perusahaan (CSV di `data/raw`) |

Uji: `task test-quality` (satu latihan: `task test-quality -- -k dq03`).
Petunjuk: `task hint -- dq03`.

Bonus (opsional): contoh dbt dengan test `unique`, `not_null`, `relationships`,
`accepted_values` di folder `dbt_example/` di root repo.

Pertanyaan interview yang sering muncul di topik ini:
- Apa bedanya pengecekan yang **memblokir** pipeline dengan yang hanya **memberi peringatan**?
- Di layer mana Anda memasang pengecekan (bronze, silver, gold), dan kenapa?
- Bagaimana Anda tahu data "hari ini" sudah lengkap sebelum dashboard dipublikasikan?
