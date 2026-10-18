"""Kunci jawaban DAG02."""

from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator


def extract_region(region: str, ds: str):
    # ds dari template, misalnya "2025-10-01". Query sumber memakai rentang tanggal ini saja.
    print(f"extract {region} untuk {ds}")


def merge(ds: str):
    print(f"merge semua region untuk {ds}")


with DAG(
    dag_id="regional_sales_backfill",
    schedule="@daily",
    start_date=pendulum.datetime(2025, 10, 1, tz="Asia/Jakarta"),
    catchup=True,
    max_active_runs=2,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=10), "depends_on_past": False},
) as dag:
    start = EmptyOperator(task_id="start")
    extract_jawa = PythonOperator(task_id="extract_jawa", python_callable=extract_region, pool="branch_db",
                                  op_kwargs={"region": "jawa", "ds": "{{ ds }}"})
    extract_sumatera = PythonOperator(task_id="extract_sumatera", python_callable=extract_region, pool="branch_db",
                                      op_kwargs={"region": "sumatera", "ds": "{{ ds }}"})
    extract_sulawesi = PythonOperator(task_id="extract_sulawesi", python_callable=extract_region, pool="branch_db",
                                      op_kwargs={"region": "sulawesi", "ds": "{{ ds }}"})
    merge_regions = PythonOperator(task_id="merge_regions", python_callable=merge, op_kwargs={"ds": "{{ ds }}"})
    end = EmptyOperator(task_id="end")

    start >> [extract_jawa, extract_sumatera, extract_sulawesi] >> merge_regions >> end
