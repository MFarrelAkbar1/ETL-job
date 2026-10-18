# de-interview-prep

Repo latihan lokal untuk interview **Data Engineer**: SQL, Python/pandas, data modeling,
dan konsep pipeline. Semua latihan coding dinilai otomatis dengan pytest. Pesan error
menjelaskan apa yang salah dari jawaban Anda tanpa membocorkan kunci jawaban.

Tidak butuh akun cloud. Internet hanya dibutuhkan sekali saat `task setup` (install library).

## Status modul

| Modul | Isi | Status |
|---|---|---|
| 1. SQL | 25 soal (mudah ke sulit), 10 berlabel PRIORITAS, mode timed | Siap |
| 2. Python dan pandas | 12 latihan, terakhir mini ETL ke star schema | Siap |
| 3. Data modeling | 5 studi kasus + rubrik, 8 latihan grain/fact/dimension | Siap |
| 4. Data quality | 8 latihan + bonus contoh dbt-duckdb | Siap |
| 5. PySpark | Butuh Java 17 (di mesin ini baru ada Java 8) | Dilewati, lihat [Install Java 17](#install-java-17-untuk-modul-5) |
| 6. Lakehouse dan Iceberg | 7 latihan PyIceberg lokal + penjelasan metadata + playground | Siap |
| 7. Kuis konsep | `quiz/quiz.html`: 80 soal pilihan ganda (12 topik) + 32 flashcard | Siap |
| 8. Airflow | 3 latihan DAG, dinilai dengan AST tanpa install Airflow | Siap |
| 9. Git, Docker, Linux | `cheatsheet/git_docker_linux.md` | Siap |

## Setup

Kebutuhan: **Python 3.12** dan **[Task](https://taskfile.dev)** (`task`).

### Windows

```powershell
# Task sudah terpasang di mesin ini. Kalau belum: winget install Task.Task
cd de-interview-prep
task setup
```

`task setup` membuat `.venv` dengan `py -3.12`, menginstall `requirements.txt`, membangkitkan
dataset (`data/generate.py`, sekitar 10 detik), dan membuat file soal SQL.

### WSL2 / Linux

```bash
sudo apt install python3.12 python3.12-venv   # Ubuntu 22.04: tambahkan dulu ppa:deadsnakes/ppa
sudo snap install task --classic              # atau lihat https://taskfile.dev/installation
cd de-interview-prep
task setup
```

> Kalau Anda pindah dari Windows ke WSL di folder yang sama, hapus `.venv` dulu lalu jalankan
> `task setup` lagi. Virtualenv Windows dan Linux tidak bisa dipakai bergantian.

## Perintah

| Perintah | Fungsi |
|---|---|
| `task setup` | Install semua dan bangkitkan dataset |
| `task test-sql` | Nilai semua soal SQL. Satu soal: `task test-sql -- -k s07` |
| `task test-python` | Nilai Modul 2. Satu latihan: `task test-python -- -k p05` |
| `task test-modeling` | Nilai latihan grain/fact/dimension |
| `task test-quality` | Nilai Modul 4 (data quality) |
| `task test-iceberg` | Nilai Modul 6 (Iceberg) |
| `task test-airflow` | Nilai Modul 8 (struktur DAG) |
| `task test-all` | Nilai semua modul |
| `task iceberg-demo` | Buat tabel Iceberg contoh dan tampilkan isi folder metadata-nya |
| `task dbt-setup` lalu `task dbt-build` | (Opsional) contoh dbt-duckdb di `dbt_example/`, memakai `.venv-dbt` terpisah |
| `task progress` | Berapa soal yang sudah lulus per modul. Detail: `task progress -- --all` |
| `task hint -- s07` | Petunjuk bertahap. Jalankan lagi untuk level berikutnya (maksimal 3) |
| `task timed` | Simulasi live test: 5 soal SQL acak, 15 menit |
| `task timed -- --priority` | Timed khusus dari 10 soal prioritas |
| `task reset -- s07` | Kosongkan lagi satu soal (`s07`, `p03`, `g`, `k02`, `dq03`, `ice03`, `dag02`, atau `all`) |
| `task quiz` | Buka kuis konsep di browser (juga bisa klik dua kali `quiz/quiz.html`) |
| `task data` | Bangkitkan ulang dataset (hasil selalu sama, seed tetap) |
| `task verify` | Untuk pembuat soal: jalankan semua test dengan kunci jawaban |

Progress tercatat otomatis setiap kali Anda menjalankan test.

## Struktur

```
data/            generate.py, KAMUS_DATA.md, warehouse.duckdb, raw/*.csv, parquet/*.parquet
exercises/       FILE YANG ANDA KERJAKAN
  m1_sql/        s01.sql ... s25.sql, INDEX.md (daftar soal, tingkat, prioritas)
  m2_python/     p01_extract.py ... p12_mini_etl.py
  m3_modeling/   kasus_01.md ... kasus_05.md, grain_fact_dim.yaml
  m4_quality/    dq01 ... dq08 (+ dq_base.py yang sudah jadi)
  m6_iceberg/    ice01 ... ice07, METADATA_ICEBERG.md (+ ice_base.py yang sudah jadi)
  m8_airflow/    dag01 ... dag03
quiz/            quiz.html (kuis + flashcard, mandiri, tanpa server)
cheatsheet/      git_docker_linux.md
dbt_example/     bonus Modul 4: proyek dbt-duckdb kecil dengan data test
solutions/       kunci jawaban dan rubrik (buka SETELAH mencoba)
hints/           petunjuk 3 level per soal
tests/           grader
tools/           progress, hint, timed, reset, iceberg_demo
```

## Cara mengerjakan

**SQL**: buka `exercises/m1_sql/s01.sql`. Soal ada di komentar header. Tulis query di bawah
baris `-- Tulis jawaban Anda DI BAWAH baris ini`, lalu `task test-sql -- -k s01`.
File boleh berisi beberapa statement; yang dinilai hasil statement terakhir (untuk S20 dan
S21 yang dinilai isi tabel akhir). Coba query secara interaktif:

```bash
.venv/Scripts/python.exe -c "import duckdb; c=duckdb.connect('data/warehouse.duckdb', read_only=True); c.sql(open('exercises/m1_sql/s01.sql').read()).show()"
```

Di Linux/WSL ganti `.venv/Scripts/python.exe` dengan `.venv/bin/python`. Ekstensi DuckDB
untuk VS Code atau DBeaver juga bisa membuka `data/warehouse.duckdb` (mode read-only).

**Python**: lengkapi fungsi di `exercises/m2_python/pXX_*.py` (hapus `raise NotImplementedError`).
P12 boleh meng-import fungsi Anda dari P01 sampai P11.

**Modul 4, 6, 8**: setiap folder punya `README.md` berisi daftar latihan dan cara mengujinya.
Untuk Iceberg, baca `METADATA_ICEBERG.md` dulu dan coba `task iceberg-demo`.

**Modeling**: isi `grain_fact_dim.yaml`, lalu `task test-modeling`. Untuk studi kasus, tulis di
bagian `## Jawaban Saya`, lalu nilai sendiri dengan rubrik di `solutions/m3_modeling/`.

## Jadwal belajar sampai Rabu

Hari ini Minggu, 18 Oktober 2026. Interview Rabu, 21 Oktober.

| Hari | Durasi | Fokus |
|---|---|---|
| **Minggu** (malam ini) | 2 sampai 3 jam | `task setup`, baca `data/KAMUS_DATA.md`. SQL S01 sampai S10. Jangan lewatkan S04 dan S05 (prioritas) |
| **Senin** | 5 sampai 6 jam | Pagi: SQL S11 sampai S19 (S11 s.d. S14, S16, S17 prioritas). Siang: Python P01 sampai P06. Sore: `task timed` satu kali, catat soal yang gagal |
| **Selasa** | 6 sampai 7 jam | Pagi: SQL S20 sampai S25 (S20, S21 prioritas). Siang: Python P07 sampai P12, lalu data quality DQ01 sampai DQ04. Sore: grain g01 sampai g08 + studi kasus 01, 02, 03 (pakai timer). Malam: `task quiz` satu putaran semua topik (20 soal), lalu `task timed -- --priority` |
| **Rabu** (pagi) | 1 sampai 2 jam | `task timed -- --priority` sekali lagi, `task quiz` mode "Ulangi soal yang pernah salah", flashcard 15 menit, baca `cheatsheet/git_docker_linux.md` dan `exercises/m6_iceberg/METADATA_ICEBERG.md`. Latih menjelaskan satu studi kasus secara lisan dalam 3 menit. Tidur cukup lebih penting daripada satu soal lagi |

Kalau masih ada waktu setelah semua di atas: DQ05 sampai DQ08, Iceberg ICE01 sampai ICE07
(sekitar 1,5 jam), Airflow DAG01 sampai DAG03 (sekitar 45 menit), dan bonus dbt.

**Jalur kilat** kalau waktu sangat terbatas: 10 soal SQL prioritas (S04, S05, S11, S12, S13,
S14, S16, S17, S20, S21), Python P04, P05, P12, grain g01 sampai g05, kasus 02 dan 03, dan satu
putaran kuis.

Tips: kerjakan dulu tanpa petunjuk selama 10 menit. Kalau buntu, buka `task hint` satu level
saja, lalu coba lagi. Bandingkan dengan `solutions/` hanya setelah lulus atau benar-benar buntu,
dan perhatikan komentar di kunci jawaban: di situ penjelasan konsep yang sering ditanyakan.

## Install Java 17 (untuk Modul 5)

Modul 5 (PySpark) dilewati karena mesin ini baru punya Java 8. Modul lain tidak terpengaruh.
Kalau ingin mengaktifkannya nanti:

```powershell
# Windows
winget install EclipseAdoptium.Temurin.17.JDK
# buka terminal baru, lalu cek:
java -version     # harus 17.x
```

```bash
# WSL2 / Ubuntu
sudo apt install openjdk-17-jdk
java -version
```

Kalau `java -version` masih menunjukkan 1.8, atur `JAVA_HOME` ke folder JDK 17 dan taruh
`%JAVA_HOME%\bin` paling depan di `PATH`. Jalankan `.venv/Scripts/python.exe tools/check_java.py`
untuk memeriksa.

## Catatan dataset

Data disimulasikan dengan seed tetap: perusahaan distributor farmasi dan consumer goods, 2024
sampai 2025, sekitar 50.000 order dan 150.000 item. Kotoran yang sengaja disisipkan: order_id
duplikat, NULL, format tanggal campur, harga negatif, kode produk beda huruf besar kecil, dan
distributor yang tidak ada di master. Detail lengkap di `data/KAMUS_DATA.md`.
