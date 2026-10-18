"""
DAG02 | Fan-out per region, aman untuk backfill
Tingkat: SEDANG

SOAL
  Tim ingin mengisi ulang (backfill) data sejak 1 Oktober 2025, per hari, dari tiga database
  region, tanpa membebani database sumber.

  - dag_id "regional_sales_backfill", schedule "@daily"
  - start_date pendulum.datetime(2025, 10, 1, tz="Asia/Jakarta"), catchup=True
  - max_active_runs=2 (paling banyak 2 tanggal diproses bersamaan)
  - default_args: retries 2, retry_delay 10 menit, depends_on_past False
  - Task:
        start             EmptyOperator
        extract_jawa      PythonOperator
        extract_sumatera  PythonOperator
        extract_sulawesi  PythonOperator
        merge_regions     PythonOperator
        end               EmptyOperator
  - Dependensi: start ke ketiga extract (paralel), ketiga extract ke merge_regions,
    merge_regions ke end.
  - Ketiga extract memakai pool="branch_db" (membatasi koneksi ke database sumber).
  - Setiap extract dan merge_regions menerima tanggal data lewat
    op_kwargs={"ds": "{{ ds }}"}, BUKAN dihitung dari waktu sekarang. Inilah yang membuat
    backfill dan rerun idempotent.

Uji     : task test-airflow -- -k dag02
Petunjuk: task hint -- dag02
"""

from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

# Tulis fungsi dan DAG Anda di bawah ini.
