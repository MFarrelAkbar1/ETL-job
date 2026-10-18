"""Pemeriksaan umum untuk test DAG."""

from dag_ast import Unknown, merged_arg
from py_check import check


def check_dag_args(info, dag_id, schedule, start, catchup):
    kw = info.dag_kwargs
    check(kw.get("dag_id") == dag_id, f"dag_id = {kw.get('dag_id')!r}, seharusnya {dag_id!r}.")
    sched = kw.get("schedule", kw.get("schedule_interval"))
    check(sched == schedule, f"schedule = {sched!r}, seharusnya {schedule!r}.")
    sd = kw.get("start_date")
    raw = info.dag_raw.get("start_date")
    src = raw is not None and __import__("ast").unparse(raw)
    check(sd is not None, "start_date belum diisi.")
    check(not (isinstance(sd, Unknown) and ("now" in sd.src or "days_ago" in sd.src)),
          f"start_date dinamis ({src}). Nilainya berubah setiap DAG di-parse; gunakan tanggal statis.")
    check(isinstance(sd, tuple) and sd[0] == "datetime" and tuple(sd[1][:3]) == start,
          f"start_date = {src}, seharusnya tanggal statis {start}.")
    check(sd[2].get("tz") == "Asia/Jakarta" if isinstance(sd, tuple) else False,
          "start_date harus memakai tz='Asia/Jakarta' supaya jadwal 02.00 berarti 02.00 WIB.")
    check(kw.get("catchup") is catchup, f"catchup = {kw.get('catchup')!r}, seharusnya {catchup}.")


def check_tasks(info, expected: dict):
    """expected: task_id -> nama operator"""
    got = {t: info.tasks[t].operator for t in info.tasks}
    missing = sorted(set(expected) - set(got))
    extra = sorted(set(got) - set(expected))
    check(not missing, f"Task yang belum ada: {missing}. Task yang ditemukan: {sorted(got)}.")
    check(not extra, f"Task yang tidak diminta: {extra}.")
    for tid, op in expected.items():
        check(got[tid] == op, f"Task {tid} memakai {got[tid]}, seharusnya {op}.")


def check_edges(info, expected: set):
    missing = sorted(expected - info.edges)
    extra = sorted(info.edges - expected)
    msg = []
    if missing:
        msg.append("Dependensi yang belum ada:\n    " + "\n    ".join(f"{a} >> {b}" for a, b in missing))
    if extra:
        msg.append("Dependensi yang tidak diminta:\n    " + "\n    ".join(f"{a} >> {b}" for a, b in extra))
    check(not msg, "Urutan task belum sesuai.\n  " + "\n  ".join(msg))


def check_timedelta(value, seconds, what):
    check(isinstance(value, tuple) and value[0] == "timedelta" and value[1] == seconds,
          f"{what} = {value!r}, seharusnya timedelta {seconds // 60} menit.")


def arg(info, tid, name):
    return merged_arg(info, info.tasks[tid], name)
