"""Kunci jawaban DAG03."""

from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.trigger_rule import TriggerRule


def check_quality(**context):
    print("cek kualitas file", context["ds_nodash"])


def load(**context):
    print("load ke warehouse")


def notify(**context):
    print("kirim alert ke on-call")


with DAG(
    dag_id="file_ingest_quality",
    schedule="0 5 * * *",
    start_date=pendulum.datetime(2025, 1, 1, tz="Asia/Jakarta"),
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
) as dag:
    wait_for_file = FileSensor(
        task_id="wait_for_file",
        filepath="/data/incoming/sales_{{ ds_nodash }}.csv",
        mode="reschedule",
        poke_interval=300,
        timeout=6 * 60 * 60,
    )
    quality_check = PythonOperator(task_id="quality_check", python_callable=check_quality, retries=0)
    load_to_warehouse = PythonOperator(task_id="load_to_warehouse", python_callable=load)
    notify_failure = PythonOperator(task_id="notify_failure", python_callable=notify,
                                    trigger_rule=TriggerRule.ONE_FAILED)

    wait_for_file >> quality_check >> load_to_warehouse
    [quality_check, load_to_warehouse] >> notify_failure
    # Kenapa wait_for_file tidak perlu langsung upstream notify_failure? Kalau sensor gagal
    # (timeout), quality_check menjadi upstream_failed. Trigger rule one_failed terpicu oleh
    # upstream langsung yang failed MAUPUN upstream_failed, jadi alert tetap jalan lewat
    # quality_check. Edge tambahan dari sensor tidak salah, hanya tidak diperlukan.
    # (Perilaku trigger rule bisa berbeda antar versi; selalu cek dokumentasi versi Anda.)
