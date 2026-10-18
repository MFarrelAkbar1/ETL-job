"""
DAG01 | DAG harian penjualan
Tingkat: MUDAH

SOAL
  Tulis DAG dengan ketentuan:
  - dag_id "daily_sales", berjalan setiap hari jam 02.00 (cron "0 2 * * *")
  - start_date STATIS: pendulum.datetime(2025, 1, 1, tz="Asia/Jakarta")
    (jangan datetime.now() atau days_ago)
  - catchup=False (DAG baru, tidak perlu mengejar run historis)
  - tags=["sales"]
  - default_args: owner "data-eng", retries 3, retry_delay 5 menit (timedelta),
    retry_exponential_backoff True
  - Tiga PythonOperator berurutan:
        extract_orders >> transform_orders >> load_fact_sales
    Masing-masing memanggil fungsi Python yang Anda definisikan di file ini
    (python_callable=nama_fungsi, bukan lambda).

Uji     : task test-airflow -- -k dag01
Petunjuk: task hint -- dag01
"""

from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator

# Tulis fungsi dan DAG Anda di bawah ini.
