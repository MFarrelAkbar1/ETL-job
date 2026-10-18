from dag_checks import arg, check_dag_args, check_edges, check_tasks, check_timedelta
from py_check import check

EX, FILE = "dag02", "dag02_regional_backfill"
EXTRACTS = ["extract_jawa", "extract_sumatera", "extract_sulawesi"]


def test_konfigurasi_dag(dag):
    check_dag_args(dag, "regional_sales_backfill", "@daily", (2025, 10, 1), True)
    check(dag.dag_kwargs.get("max_active_runs") == 2,
          f"max_active_runs = {dag.dag_kwargs.get('max_active_runs')!r}, seharusnya 2 (backfill tidak boleh menyerbu sumber).")
    da = dag.dag_kwargs.get("default_args") or {}
    check(da.get("retries") == 2, f"default_args retries = {da.get('retries')!r}, seharusnya 2.")
    check_timedelta(da.get("retry_delay"), 600, "retry_delay")
    check(da.get("depends_on_past") is False, "default_args depends_on_past harus False.")


def test_fan_out_fan_in(dag):
    check_tasks(dag, {"start": "EmptyOperator", "end": "EmptyOperator", "merge_regions": "PythonOperator",
                      **{e: "PythonOperator" for e in EXTRACTS}})
    exp = {("start", e) for e in EXTRACTS} | {(e, "merge_regions") for e in EXTRACTS} | {("merge_regions", "end")}
    check_edges(dag, exp)


def test_pool_dan_template(dag):
    for e in EXTRACTS:
        check(arg(dag, e, "pool") == "branch_db", f"{e}: pool = {arg(dag, e, 'pool')!r}, seharusnya 'branch_db'.")
    for t in EXTRACTS + ["merge_regions"]:
        ok = arg(dag, t, "op_kwargs")
        check(isinstance(ok, dict) and isinstance(ok.get("ds"), str) and "{{ ds }}" in ok.get("ds").replace("{{ds}}", "{{ ds }}"),
              f"{t}: op_kwargs harus berisi 'ds': '{{{{ ds }}}}' supaya tanggal data mengikuti logical date. Didapat {ok!r}.")
    check(arg(dag, "merge_regions", "pool") in (None, "default_pool"),
          "merge_regions tidak perlu pool branch_db (tidak menyentuh database sumber).")
