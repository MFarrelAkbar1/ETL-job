# Cheatsheet Git, Docker, Linux (untuk Data Engineer)

## Git

| Perintah | Fungsi |
|---|---|
| `git switch -c feat/dq-checks` | Buat branch baru dan pindah ke sana |
| `git add -p` | Pilih potongan perubahan yang di-stage, satu per satu |
| `git commit -m "Tambah check unique order_id"` | Commit dengan pesan yang menjelaskan *apa* dan *kenapa* |
| `git fetch` lalu `git rebase origin/main` | Perbarui branch dari main dengan histori linear |
| `git merge --no-ff feat/x` | Merge dengan commit merge (histori branch tetap terlihat) |
| `git log --oneline --graph -20` | Lihat histori ringkas |
| `git diff --staged` | Lihat apa yang akan di-commit |
| `git stash push -m "wip"` / `git stash pop` | Simpan perubahan sementara |
| `git restore file.py` / `git restore --staged file.py` | Buang perubahan di file / batalkan stage |
| `git revert <sha>` | Batalkan commit dengan commit baru (aman untuk branch bersama) |
| `git reset --soft HEAD~1` | Batalkan commit terakhir, perubahan tetap di-stage (hanya branch lokal) |
| `git cherry-pick <sha>` | Ambil satu commit dari branch lain (misalnya hotfix) |
| `git blame -L 10,30 dag.py` | Siapa mengubah baris tertentu |
| `git bisect start` / `good` / `bad` | Cari commit yang memasukkan bug dengan binary search |

Sering ditanya: **merge vs rebase** (rebase menulis ulang histori, jangan rebase branch yang
sudah dipakai orang lain); **revert vs reset** (revert aman di remote); jangan commit secret
(pakai `.gitignore`, secret manager, dan pre-commit hook); data besar tidak masuk Git.

## Docker

| Perintah | Fungsi |
|---|---|
| `docker build -t etl:1.0 .` | Build image dari Dockerfile |
| `docker run --rm -it -v "$PWD/data:/app/data" -e ENV=dev etl:1.0` | Jalankan container, mount folder, set env |
| `docker run -d -p 5432:5432 --name pg -e POSTGRES_PASSWORD=x postgres:16` | Database lokal untuk testing |
| `docker ps` / `docker ps -a` | Container yang jalan / semua |
| `docker logs -f pg` | Ikuti log container |
| `docker exec -it pg psql -U postgres` | Masuk ke container yang sedang jalan |
| `docker compose up -d` / `docker compose down -v` | Jalankan / hentikan stack (misalnya Airflow + Postgres) |
| `docker image ls` / `docker system prune` | Lihat image / bersihkan yang tidak terpakai |

Dockerfile yang baik untuk job Python:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt   # layer ini di-cache kalau requirements tidak berubah
COPY src/ ./src/
USER 1000                                              # jangan jalan sebagai root
CMD ["python", "-m", "src.etl"]
```

Sering ditanya: **image vs container**; **layer caching** (salin requirements dulu, kode
belakangan); **volume vs bind mount**; konfigurasi lewat environment variable, bukan dimasukkan
ke image; satu proses per container.

## Linux

| Perintah | Fungsi |
|---|---|
| `head -5 file.csv` / `tail -f app.log` | Lihat awal file / ikuti log |
| `wc -l file.csv` | Hitung baris (rekonsiliasi cepat) |
| `cut -d, -f1 orders.csv \| sort \| uniq -d \| head` | Cari nilai kolom pertama yang duplikat |
| `awk -F, 'NR>1 {s+=$5} END {print s}' items.csv` | Jumlahkan kolom ke-5 (lewati header) |
| `grep -c "ERROR" app.log` / `grep -rn "TODO" src/` | Hitung baris error / cari teks rekursif |
| `sed -n '100,120p' file.csv` | Tampilkan baris 100 sampai 120 |
| `find /data -name "*.parquet" -mtime -1` | File Parquet yang berubah 24 jam terakhir |
| `du -sh /data/*` / `df -h` | Ukuran folder / sisa disk (penyebab umum job gagal) |
| `ps aux \| grep python` / `top` / `htop` | Proses yang jalan / pemakaian CPU dan memori |
| `kill -15 <pid>` lalu `kill -9 <pid>` | Hentikan proses (sopan dulu, paksa kalau perlu) |
| `chmod +x run.sh` / `chown user:group file` | Izin eksekusi / kepemilikan |
| `export DB_HOST=localhost` / `env \| grep DB_` | Set dan lihat environment variable |
| `nohup python etl.py > etl.log 2>&1 &` | Jalankan di background, stdout dan stderr ke file |
| `crontab -e` dengan `0 2 * * * /opt/etl/run.sh` | Jadwal harian jam 02.00 (sebelum ada orchestrator) |
| `ssh user@host` / `scp file user@host:/tmp/` | Login dan salin file ke server |
| `curl -s https://api/x \| jq '.items[0]'` | Panggil API dan baca JSON |
| `gzip -dc big.csv.gz \| head` | Intip file terkompresi tanpa ekstrak |

Format cron: `menit jam tanggal bulan hari_minggu`, contoh `30 1 * * 1-5` = 01.30 Senin sampai
Jumat. Exit code `0` = sukses; pakai `set -euo pipefail` di awal script bash supaya script
berhenti saat ada perintah yang gagal.
