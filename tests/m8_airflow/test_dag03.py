from dag_checks import arg, check_dag_args, check_edges, check_tasks, check_timedelta
from py_check import check

EX, FILE = "dag03", "dag03_file_sensor_quality"


def test_konfigurasi_dag(dag):
    check_dag_args(dag, "file_ingest_quality", "0 5 * * *", (2025, 1, 1), False)
    da = dag.dag_kwargs.get("default_args") or {}
    check(da.get("retries") == 1, f"default_args retries = {da.get('retries')!r}, seharusnya 1.")
    check_timedelta(da.get("retry_delay"), 300, "retry_delay")


def test_sensor(dag):
    check_tasks(dag, {"wait_for_file": "FileSensor", "quality_check": "PythonOperator",
                      "load_to_warehouse": "PythonOperator", "notify_failure": "PythonOperator"})
    s = dag.tasks["wait_for_file"].kwargs
    check(s.get("filepath") == "/data/incoming/sales_{{ ds_nodash }}.csv", f"filepath = {s.get('filepath')!r}.")
    mode = s.get("mode")
    check(mode == "reschedule", ("mode belum diisi, jadi memakai default 'poke'" if mode is None else f"mode = {mode!r}")
          + ". Mode 'poke' menahan worker slot selama menunggu berjam-jam; pakai 'reschedule'.")
    check(s.get("poke_interval") == 300, f"poke_interval = {s.get('poke_interval')!r}, seharusnya 300 detik.")
    check(s.get("timeout") == 21600, f"timeout = {s.get('timeout')!r}, seharusnya 21600 detik (6 jam).")


def test_retry_dan_trigger_rule(dag):
    check(arg(dag, "quality_check", "retries") == 0,
          f"quality_check: retries efektif {arg(dag, 'quality_check', 'retries')}, seharusnya 0 (override default_args).")
    check(arg(dag, "load_to_warehouse", "retries") == 1, "load_to_warehouse harus tetap memakai retries 1 dari default_args.")
    tr = arg(dag, "notify_failure", "trigger_rule")
    check(tr == "one_failed", f"notify_failure trigger_rule = {tr!r}, seharusnya 'one_failed'. Default 'all_success' membuat alert hanya jalan saat semuanya SUKSES.")


def test_urutan(dag):
    check_edges(dag, {("wait_for_file", "quality_check"), ("quality_check", "load_to_warehouse"),
                      ("quality_check", "notify_failure"), ("load_to_warehouse", "notify_failure")})
