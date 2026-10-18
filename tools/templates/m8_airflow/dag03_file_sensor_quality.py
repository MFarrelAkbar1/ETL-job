"""
DAG03 | Menunggu file, cek kualitas, alert kalau gagal
Tingkat: SEDANG

SOAL
  Distributor mengirim file CSV setiap pagi. File bisa terlambat sampai 6 jam.

  - dag_id "file_ingest_quality", schedule "0 5 * * *",
    start_date pendulum.datetime(2025, 1, 1, tz="Asia/Jakarta"), catchup=False
  - default_args: retries 1, retry_delay 5 menit
  - Task:
        wait_for_file      FileSensor
                             filepath="/data/incoming/sales_{{ ds_nodash }}.csv"
                             mode="reschedule"      (tidak menahan worker slot selama menunggu)
                             poke_interval=300      (cek setiap 5 menit)
                             timeout=21600          (menyerah setelah 6 jam; boleh 6 * 60 * 60)
        quality_check      PythonOperator, retries=0 (data rusak tidak akan sembuh dengan retry)
        load_to_warehouse  PythonOperator
        notify_failure     PythonOperator, trigger_rule="one_failed"
                           (boleh juga TriggerRule.ONE_FAILED)
  - Dependensi:
        wait_for_file >> quality_check >> load_to_warehouse
        quality_check dan load_to_warehouse sama-sama upstream dari notify_failure
    Pikirkan: kenapa wait_for_file TIDAK dijadikan upstream langsung notify_failure?

Uji     : task test-airflow -- -k dag03
Petunjuk: task hint -- dag03
"""

from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor

# Tulis fungsi dan DAG Anda di bawah ini.
