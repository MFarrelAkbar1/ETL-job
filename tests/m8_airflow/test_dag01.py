from dag_checks import arg, check_dag_args, check_edges, check_tasks, check_timedelta
from py_check import check

EX, FILE = "dag01", "dag01_daily_sales"
TASKS = ["extract_orders", "transform_orders", "load_fact_sales"]


def test_konfigurasi_dag(dag):
    check_dag_args(dag, "daily_sales", "0 2 * * *", (2025, 1, 1), False)
    check(dag.dag_kwargs.get("tags") == ["sales"], f"tags = {dag.dag_kwargs.get('tags')!r}, seharusnya ['sales'].")


def test_default_args(dag):
    da = dag.dag_kwargs.get("default_args")
    check(isinstance(da, dict), "default_args belum diisi (harus dict).")
    check(da.get("owner") == "data-eng", f"owner = {da.get('owner')!r}.")
    check(da.get("retries") == 3, f"retries = {da.get('retries')!r}, seharusnya 3.")
    check_timedelta(da.get("retry_delay"), 300, "retry_delay")
    check(da.get("retry_exponential_backoff") is True, "retry_exponential_backoff harus True.")


def test_task_dan_urutan(dag):
    check_tasks(dag, {t: "PythonOperator" for t in TASKS})
    check_edges(dag, {("extract_orders", "transform_orders"), ("transform_orders", "load_fact_sales")})
    for t in TASKS:
        cb = dag.tasks[t].raw.get("python_callable")
        name = getattr(cb, "id", None)
        check(name in dag.functions,
              f"{t}: python_callable harus nama fungsi yang didefinisikan di file ini (bukan lambda), didapat {cb and __import__('ast').unparse(cb)}.")
        check(arg(dag, t, "retries") == 3, f"{t}: retries efektif {arg(dag, t, 'retries')}, seharusnya 3 dari default_args.")
