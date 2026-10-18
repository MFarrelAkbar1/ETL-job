# Modul 8: Airflow (tanpa install Airflow)

Tulis 3 file DAG seperti untuk Airflow sungguhan. File **tidak dijalankan**; test membaca
strukturnya dengan AST (urutan task, retries, schedule, catchup, trigger rule, dan lainnya).
Editor mungkin menandai `import airflow` sebagai error karena Airflow tidak terpasang. Itu wajar.

Aturan penulisan supaya bisa dianalisis:
- Gunakan `with DAG(...) as dag:` atau `dag = DAG(...)`.
- Gunakan operator klasik (`PythonOperator`, `EmptyOperator`, `FileSensor`) yang di-assign ke
  variabel, dengan `task_id="..."` berupa string literal.
- Dependensi dengan `>>`, `<<`, list (`a >> [b, c]`), `set_downstream`, atau `chain(...)`.
- Nilai seperti `default_args` boleh berupa variabel di level modul.

| No | File | Konsep |
|---|---|---|
| DAG01 | `dag01_daily_sales.py` | schedule cron, start_date statis, catchup, retries, urutan linear |
| DAG02 | `dag02_regional_backfill.py` | fan-out/fan-in, backfill aman, max_active_runs, pool, template `{{ ds }}` |
| DAG03 | `dag03_file_sensor_quality.py` | sensor mode reschedule, override retries, trigger_rule untuk alert |

Uji: `task test-airflow` (satu latihan: `task test-airflow -- -k dag02`).
Petunjuk: `task hint -- dag02`.
