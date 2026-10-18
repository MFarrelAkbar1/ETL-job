"""Kunci jawaban DAG01."""

from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator


def extract(**context):
    print("extract", context["ds"])


def transform(**context):
    print("transform", context["ds"])


def load(**context):
    print("load", context["ds"])


default_args = {
    "owner": "data-eng",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
}

with DAG(
    dag_id="daily_sales",
    schedule="0 2 * * *",
    start_date=pendulum.datetime(2025, 1, 1, tz="Asia/Jakarta"),
    catchup=False,
    default_args=default_args,
    tags=["sales"],
) as dag:
    extract_orders = PythonOperator(task_id="extract_orders", python_callable=extract)
    transform_orders = PythonOperator(task_id="transform_orders", python_callable=transform)
    load_fact_sales = PythonOperator(task_id="load_fact_sales", python_callable=load)

    extract_orders >> transform_orders >> load_fact_sales
