"""Analisis struktur file DAG Airflow lewat AST, tanpa meng-import atau menjalankan Airflow.

Yang dikenali:
  - `with DAG(...) as dag:` atau `dag = DAG(...)` (argumen posisi pertama = dag_id)
  - task = pemanggilan class yang namanya berakhiran Operator atau Sensor, dengan task_id=...
  - dependensi: a >> b, a << b, rantai a >> [b, c] >> d, a.set_downstream(b), a.set_upstream(b),
    dan chain(a, b, c)
  - nilai keyword dievaluasi secara statis: konstanta, list/dict/tuple, aritmetika konstanta,
    timedelta(...), datetime/pendulum.datetime(...), TriggerRule.X, dan nama variabel modul
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


class Unknown:
    def __init__(self, src: str):
        self.src = src

    def __repr__(self):
        return f"<tidak bisa dievaluasi: {self.src}>"


@dataclass
class Task:
    var: str | None
    task_id: str
    operator: str
    kwargs: dict
    raw: dict  # node AST mentah per keyword


@dataclass
class DagInfo:
    dag_kwargs: dict = field(default_factory=dict)
    dag_raw: dict = field(default_factory=dict)
    tasks: dict = field(default_factory=dict)          # task_id -> Task
    edges: set = field(default_factory=set)            # (upstream_task_id, downstream_task_id)
    functions: set = field(default_factory=set)        # nama def di level modul
    problems: list = field(default_factory=list)
    n_dags: int = 0


class _Eval:
    def __init__(self, names: dict):
        self.names = names

    def __call__(self, node):
        if node is None:
            return None
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            return [self(e) for e in node.elts]
        if isinstance(node, ast.Dict):
            return {self(k): self(v) for k, v in zip(node.keys, node.values)}
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            v = self(node.operand)
            return -v if isinstance(v, (int, float)) else Unknown(ast.unparse(node))
        if isinstance(node, ast.BinOp):
            a, b = self(node.left), self(node.right)
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                ops = {ast.Add: a + b, ast.Sub: a - b, ast.Mult: a * b}
                for t, v in ops.items():
                    if isinstance(node.op, t):
                        return v
            if isinstance(a, dict) and isinstance(b, dict) and isinstance(node.op, ast.BitOr):
                return {**a, **b}
            return Unknown(ast.unparse(node))
        if isinstance(node, ast.Name):
            if node.id in self.names:
                return self(self.names[node.id])
            return Unknown(node.id)
        if isinstance(node, ast.Attribute):
            # TriggerRule.ONE_FAILED -> "one_failed"
            if isinstance(node.value, ast.Name) and node.value.id == "TriggerRule":
                return node.attr.lower()
            return Unknown(ast.unparse(node))
        if isinstance(node, ast.Call):
            fname = _call_name(node)
            if fname == "timedelta":
                kw = {k.arg: self(k.value) for k in node.keywords}
                units = {"weeks": 604800, "days": 86400, "hours": 3600, "minutes": 60, "seconds": 1}
                pos = [self(a) for a in node.args]
                total = 0
                for i, v in enumerate(pos):
                    total += v * [86400, 1][i] if i < 2 else 0
                for k, v in kw.items():
                    if k in units and isinstance(v, (int, float)):
                        total += v * units[k]
                return ("timedelta", total)
            if fname in ("datetime", "pendulum.datetime", "datetime.datetime"):
                args = [self(a) for a in node.args]
                kw = {k.arg: self(k.value) for k in node.keywords}
                return ("datetime", tuple(args), kw)
            if fname in ("dict",):
                return {k.arg: self(k.value) for k in node.keywords}
            return Unknown(ast.unparse(node))
        if isinstance(node, ast.JoinedStr):
            return Unknown(ast.unparse(node))
        return Unknown(ast.unparse(node))


def _call_name(node: ast.Call) -> str:
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        base = f.value.id if isinstance(f.value, ast.Name) else ""
        return f"{base}.{f.attr}" if base else f.attr
    return ""


def _short(name: str) -> str:
    return name.split(".")[-1]


def analyze(path: Path) -> DagInfo:
    info = DagInfo()
    src = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        info.problems.append(f"File tidak valid sebagai Python (baris {e.lineno}): {e.msg}")
        return info

    # assignment level modul untuk resolusi nama (misalnya default_args = {...})
    names: dict[str, ast.AST] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            names[node.targets[0].id] = node.value
        if isinstance(node, ast.FunctionDef):
            info.functions.add(node.name)
    ev = _Eval(names)

    var_to_task: dict[str, str] = {}

    def register_task(call: ast.Call, var: str | None):
        op = _short(_call_name(call))
        kw_raw = {k.arg: k.value for k in call.keywords if k.arg}
        tid = ev(kw_raw.get("task_id"))
        if not isinstance(tid, str):
            info.problems.append(f"{op} tanpa task_id string literal: {ast.unparse(call)[:60]}")
            return None
        if tid in info.tasks:
            info.problems.append(f"task_id '{tid}' dipakai lebih dari sekali.")
        info.tasks[tid] = Task(var, tid, op, {k: ev(v) for k, v in kw_raw.items()}, kw_raw)
        if var:
            var_to_task[var] = tid
        return tid

    def is_task_call(node) -> bool:
        return isinstance(node, ast.Call) and _short(_call_name(node)).endswith(("Operator", "Sensor"))

    def register_dag(call: ast.Call):
        info.n_dags += 1
        raw = {k.arg: k.value for k in call.keywords if k.arg}
        if call.args:
            raw.setdefault("dag_id", call.args[0])
        info.dag_raw = raw
        info.dag_kwargs = {k: ev(v) for k, v in raw.items()}

    # pass 1: DAG dan task
    for node in ast.walk(tree):
        if isinstance(node, ast.With):
            for item in node.items:
                if isinstance(item.context_expr, ast.Call) and _short(_call_name(item.context_expr)) == "DAG":
                    register_dag(item.context_expr)
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            if _short(_call_name(node.value)) == "DAG":
                register_dag(node.value)
            elif is_task_call(node.value):
                var = node.targets[0].id if isinstance(node.targets[0], ast.Name) else None
                register_task(node.value, var)
    # task yang dibuat tanpa assignment (misalnya langsung di ekspresi >>)
    assigned_calls = {id(n.value) for n in ast.walk(tree) if isinstance(n, ast.Assign)}
    for node in ast.walk(tree):
        if is_task_call(node) and id(node) not in assigned_calls and "task_id" in {k.arg for k in node.keywords}:
            tid = ev(next(k.value for k in node.keywords if k.arg == "task_id"))
            if isinstance(tid, str) and tid not in info.tasks:
                register_task(node, None)

    # pass 2: dependensi
    def resolve(node) -> list[str]:
        if isinstance(node, ast.Name):
            if node.id in var_to_task:
                return [var_to_task[node.id]]
            info.problems.append(f"Nama '{node.id}' di dependensi bukan task yang dikenal.")
            return []
        if isinstance(node, (ast.List, ast.Tuple)):
            out = []
            for e in node.elts:
                out += resolve(e)
            return out
        if is_task_call(node):
            tid = ev(next((k.value for k in node.keywords if k.arg == "task_id"), None))
            return [tid] if isinstance(tid, str) else []
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.RShift, ast.LShift)):
            return handle_shift(node)
        info.problems.append(f"Dependensi tidak dikenali: {ast.unparse(node)[:60]}")
        return []

    def handle_shift(node: ast.BinOp) -> list[str]:
        # a >> b mengembalikan b (supaya rantai a >> b >> c jalan); a << b mengembalikan b
        left = resolve(node.left)
        right = resolve(node.right)
        for l in left:
            for r in right:
                info.edges.add((l, r) if isinstance(node.op, ast.RShift) else (r, l))
        return right

    for node in ast.walk(tree):
        if isinstance(node, ast.Expr):
            v = node.value
            if isinstance(v, ast.BinOp) and isinstance(v.op, (ast.RShift, ast.LShift)):
                handle_shift(v)
            elif isinstance(v, ast.Call):
                name = _call_name(v)
                if name.endswith(("set_downstream", "set_upstream")) and isinstance(v.func, ast.Attribute):
                    src_ids = resolve(v.func.value)
                    for a in v.args:
                        for t in resolve(a):
                            for s in src_ids:
                                info.edges.add((s, t) if name.endswith("set_downstream") else (t, s))
                elif _short(name) == "chain":
                    groups = [resolve(a) for a in v.args]
                    for g1, g2 in zip(groups, groups[1:]):
                        for a in g1:
                            for b in g2:
                                info.edges.add((a, b))
    return info


def merged_arg(info: DagInfo, task: Task, name: str):
    """Nilai argumen task: dari task sendiri, kalau tidak ada dari default_args DAG."""
    if name in task.kwargs:
        return task.kwargs[name]
    da = info.dag_kwargs.get("default_args")
    if isinstance(da, dict):
        return da.get(name)
    return None
