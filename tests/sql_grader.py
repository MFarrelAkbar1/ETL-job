"""Mesin penilai soal SQL.

Prinsip: pesan error menjelaskan APA yang salah dari hasil Anda (kolom, jumlah baris,
NULL, total angka, urutan, baris yang tidak seharusnya ada), tanpa menampilkan isi
kunci jawaban.
"""

from __future__ import annotations

import re
import threading
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import pytest
import sqlglot
from sqlglot import exp

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "warehouse.duckdb"
QUERY_TIMEOUT_S = 60
FLOAT_TOL = 0.011


# --------------------------------------------------------------------------
# Membaca dan menjalankan SQL
# --------------------------------------------------------------------------
def strip_comments(sql: str) -> str:
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    lines = []
    for line in sql.splitlines():
        # buang komentar "--" yang tidak berada di dalam string literal
        out, in_str = [], False
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == "'":
                in_str = not in_str
            if not in_str and line.startswith("--", i):
                break
            out.append(ch)
            i += 1
        lines.append("".join(out))
    return "\n".join(lines).strip()


def read_answer(path: Path) -> str:
    if not path.exists():
        pytest.fail(f"File jawaban tidak ditemukan: {path}", pytrace=False)
    sql = strip_comments(path.read_text(encoding="utf-8"))
    if not sql.strip(" ;\n\t"):
        pytest.fail(f"Belum dikerjakan: {path.name} masih kosong (hanya berisi komentar soal).",
                    pytrace=False)
    return sql


def open_readonly() -> duckdb.DuckDBPyConnection:
    if not DB_PATH.exists():
        pytest.exit("data/warehouse.duckdb belum ada. Jalankan dulu: task setup", returncode=2)
    return duckdb.connect(str(DB_PATH), read_only=True)


def open_sandbox(tables: list[str]) -> duckdb.DuckDBPyConnection:
    """Koneksi in-memory berisi salinan tabel yang boleh dimodifikasi (untuk soal DML)."""
    con = duckdb.connect()
    con.execute(f"ATTACH '{DB_PATH.as_posix()}' AS src (READ_ONLY)")
    for t in tables:
        con.execute(f"CREATE TABLE {t} AS FROM src.{t}")
    con.execute("DETACH src")
    return con


def execute(con, sql: str, who: str = "Anda") -> pd.DataFrame | None:
    timer = threading.Timer(QUERY_TIMEOUT_S, con.interrupt)
    timer.start()
    try:
        rel = con.execute(sql)
        try:
            return rel.df()
        except (duckdb.InvalidInputException, duckdb.Error):
            return None
    except duckdb.InterruptException:
        pytest.fail(f"Query {who} dihentikan setelah {QUERY_TIMEOUT_S} detik. Kemungkinan ada JOIN "
                    "tanpa kondisi yang benar (cartesian product) atau scan berulang.", pytrace=False)
    except duckdb.Error as e:
        pytest.fail(f"Query {who} error saat dijalankan DuckDB:\n  {type(e).__name__}: {e}",
                    pytrace=False)
    finally:
        timer.cancel()


# --------------------------------------------------------------------------
# Normalisasi dan perbandingan
# --------------------------------------------------------------------------
def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=range(len(df)))
    for col in df.columns:
        s = df[col].reset_index(drop=True)
        if pd.api.types.is_bool_dtype(s):
            out[col] = s.astype(object)
        elif pd.api.types.is_numeric_dtype(s):
            out[col] = pd.to_numeric(s, errors="coerce").astype(float)
        elif pd.api.types.is_datetime64_any_dtype(s):
            ts = pd.to_datetime(s)
            fmt = "%Y-%m-%d" if (ts.dropna().dt.normalize() == ts.dropna()).all() else "%Y-%m-%d %H:%M:%S"
            out[col] = ts.dt.strftime(fmt).where(ts.notna(), None)
        else:
            def conv(v):
                if v is None or (isinstance(v, float) and np.isnan(v)) or v is pd.NaT:
                    return None
                if hasattr(v, "isoformat") and not isinstance(v, str):
                    return str(v)[:19] if " " in str(v) else str(v)
                if isinstance(v, (int, float, np.number)) and not isinstance(v, bool):
                    return float(v)
                return v
            out[col] = s.map(conv).astype(object)
    return out


def _num_cols(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if df[c].dtype == float]


def _mismatch(u: pd.DataFrame, e: pd.DataFrame, num_cols: list[str]) -> pd.DataFrame:
    """Matriks boolean: True kalau sel u berbeda dengan sel e (vektorisasi, cepat untuk data besar)."""
    out = {}
    for c in e.columns:
        un, en = u[c].isna(), e[c].isna()
        if c in num_cols:
            uv = pd.to_numeric(u[c], errors="coerce")
            tol = np.maximum(FLOAT_TOL, e[c].abs() * 1e-9)
            diff = ((uv - e[c]).abs() > tol) & ~un & ~en
            diff |= uv.isna() & ~un  # nilai bukan angka di kolom angka
        else:
            diff = (u[c].astype(object) != e[c].astype(object)) & ~un & ~en
        out[c] = diff | (un != en)
    return pd.DataFrame(out)


def _first_bad(u: pd.DataFrame, e: pd.DataFrame, num_cols: list[str]):
    mm = _mismatch(u, e, num_cols)
    rows = mm.any(axis=1).to_numpy()
    if not rows.any():
        return None
    i = int(rows.argmax())
    return i, [c for c in mm.columns if mm.iloc[i][c]]


def _sorted(df: pd.DataFrame) -> pd.DataFrame:
    key = pd.DataFrame(index=df.index)
    for j, c in enumerate(df.columns):
        if df[c].dtype == float:
            key[j] = df[c].round(1).fillna(np.inf)
        else:
            key[j] = df[c].map(lambda v: "￿" if v is None else str(v))
    order = key.sort_values(list(key.columns), kind="mergesort").index
    return df.loc[order].reset_index(drop=True)


def _fmt_row(row: pd.Series) -> str:
    parts = []
    for c, v in row.items():
        if v is None or (isinstance(v, float) and np.isnan(v)):
            v = "NULL"
        elif isinstance(v, float):
            v = int(v) if float(v).is_integer() else round(v, 2)
        parts.append(f"{c}={v}")
    return "{" + ", ".join(parts) + "}"


def frames_match(user: pd.DataFrame, expected: pd.DataFrame, ordered: bool) -> bool:
    if [c.lower() for c in user.columns] != [c.lower() for c in expected.columns]:
        return False
    if len(user) != len(expected):
        return False
    u, e = _normalize(user), _normalize(expected)
    u.columns = e.columns
    if not ordered:
        u, e = _sorted(u), _sorted(e)
    return _first_bad(u, e, _num_cols(e)) is None


def diagnose(user: pd.DataFrame, expected: pd.DataFrame, ordered: bool) -> list[str]:
    """Daftar pesan dalam Bahasa Indonesia. Kosong berarti hasil sudah benar."""
    msgs: list[str] = []
    ucols = [c.lower() for c in user.columns]
    ecols = [c.lower() for c in expected.columns]
    if ucols != ecols:
        missing = [c for c in ecols if c not in ucols]
        extra = [c for c in ucols if c not in ecols]
        m = "Kolom output belum sesuai."
        if missing:
            m += f"\n  Kolom yang belum ada: {missing}"
        if extra:
            m += f"\n  Kolom yang tidak diminta: {extra}"
        if not missing and not extra:
            m += f"\n  Nama kolom sudah benar tapi URUTANNYA beda. Urutan Anda: {ucols}"
        m += f"\n  Kolom yang diminta (urut): {ecols}"
        return [m]

    u, e = _normalize(user), _normalize(expected)
    u.columns = e.columns
    num = _num_cols(e)

    if len(u) != len(e):
        arah = "lebih banyak" if len(u) > len(e) else "lebih sedikit"
        msgs.append(f"Jumlah baris: hasil Anda {len(u):,} baris, {arah} dari yang seharusnya ({len(e):,}).")
        # duplikat pada kolom non-angka sering jadi penyebab
        key_cols = [c for c in e.columns if c not in num]
        if key_cols and len(u) > len(e):
            dups = u.duplicated(subset=key_cols).sum()
            if dups and not e.duplicated(subset=key_cols).any():
                msgs.append(f"  Ada {dups:,} baris duplikat pada kombinasi kolom {key_cols}. "
                            "Cek JOIN yang menggandakan baris atau deduplikasi yang belum dilakukan.")

    for c in e.columns:
        un, en = u[c].isna().sum(), e[c].isna().sum()
        if un != en:
            msgs.append(f"Kolom '{c}': hasil Anda punya {un:,} nilai NULL, seharusnya {en:,}.")

    for c in num:
        if c not in u.columns or u[c].dtype != float:
            continue
        us, es = u[c].sum(skipna=True), e[c].sum(skipna=True)
        if abs(us - es) > max(FLOAT_TOL * max(len(e), 1), abs(es) * 1e-9):
            if es != 0:
                pct = (us - es) / abs(es) * 100
                arah = "lebih besar" if pct > 0 else "lebih kecil"
                msgs.append(f"Kolom '{c}': total seluruh baris {abs(pct):.2f}% {arah} dari seharusnya.")
            else:
                msgs.append(f"Kolom '{c}': total seluruh baris seharusnya 0.")

    if msgs:
        extra_rows = _rows_not_in(u, e, num)
        if extra_rows:
            msgs.append("Contoh baris dari hasil Anda yang tidak ada di jawaban benar:\n    "
                        + "\n    ".join(extra_rows))
        elif len(u) == len(e):
            us_, es_ = _sorted(u), _sorted(e)
            fb = _first_bad(us_, es_, num)
            if fb:
                msgs.append(f"Contoh baris Anda yang nilainya salah (kolom {fb[1]}): {_fmt_row(us_.iloc[fb[0]])}")
        return msgs

    # jumlah baris sama dan total sama: cek isi
    us_, es_ = _sorted(u), _sorted(e)
    fb = _first_bad(us_, es_, num)
    if fb:
        msgs.append("Jumlah baris dan total angka mirip, tapi ada nilai yang berbeda.\n"
                    f"  Kolom yang berbeda: {fb[1]}\n"
                    f"  Contoh baris Anda: {_fmt_row(us_.iloc[fb[0]])}")
        return msgs

    if ordered:
        fb = _first_bad(u, e, num)
        if fb:
            msgs.append("Isi hasil sudah BENAR, tetapi urutan baris belum sesuai permintaan "
                        f"(pertama kali beda di baris ke-{fb[0] + 1}). Cek ORDER BY, termasuk tie-breaker.")
    return msgs


def _rows_not_in(u: pd.DataFrame, e: pd.DataFrame, num: list[str], limit: int = 3) -> list[str]:
    key_cols = [c for c in e.columns if c not in num]
    if not key_cols:
        return []
    ek = set(map(tuple, e[key_cols].astype(str).itertuples(index=False)))
    uk = list(map(tuple, u[key_cols].astype(str).itertuples(index=False)))
    out = []
    for i, k in enumerate(uk):
        if k not in ek:
            out.append(_fmt_row(u.iloc[i]))
            if len(out) >= limit:
                break
    return out


# --------------------------------------------------------------------------
# Aturan statis untuk soal "query lambat"
# --------------------------------------------------------------------------
def static_violations(sql: str, rules: dict) -> list[str]:
    try:
        trees = [t for t in sqlglot.parse(sql, read="duckdb") if t is not None]
    except sqlglot.errors.ParseError as e:
        return [f"Query tidak bisa dianalisis oleh sqlglot ({e.__class__.__name__}). "
                "Pastikan sintaks SQL standar."]
    msgs = []
    tree = trees[-1]
    all_selects = list(tree.find_all(exp.Select))

    if rules.get("no_subquery_in_where_select"):
        for node in tree.find_all(exp.Where, exp.Having):
            if node.find(exp.Select):
                msgs.append("Masih ada subquery di dalam WHERE/HAVING. Hitung nilai pembanding sekali "
                            "saja (CTE + JOIN atau window function).")
                break
        for sel in all_selects:
            if any(p.find(exp.Select) for p in sel.expressions):
                msgs.append("Masih ada subquery di dalam daftar SELECT (scalar subquery).")
                break

    for table, limit in rules.get("max_table_refs", {}).items():
        n = sum(1 for t in tree.find_all(exp.Table) if t.name.lower() == table)
        if n > limit:
            msgs.append(f"Tabel {table} disebut {n} kali, maksimal {limit}. Gabungkan perhitungan ke "
                        "satu kali scan (agregasi kondisional dengan FILTER atau CASE WHEN).")

    if rules.get("no_union") and tree.find(exp.Union):
        msgs.append("Tidak boleh memakai UNION untuk soal ini.")

    if rules.get("no_select_distinct"):
        if any(s.args.get("distinct") for s in all_selects):
            msgs.append("Masih memakai SELECT DISTINCT. Di sini DISTINCT hanya menambal duplikat dari "
                        "window function; pakai GROUP BY biasa.")

    if rules.get("no_window") and tree.find(exp.Window):
        msgs.append("Masih memakai window function (OVER ...). Untuk total per grup cukup GROUP BY.")

    if rules.get("no_order_in_subquery"):
        root_selects = {id(tree)} | ({id(tree.this)} if isinstance(tree, exp.Union) else set())
        for s in all_selects:
            if id(s) not in root_selects and s.args.get("order"):
                msgs.append("Ada ORDER BY di dalam subquery/CTE. ORDER BY di dalam subquery tidak menjamin "
                            "urutan hasil akhir dan hanya menambah biaya sort.")
                break

    col = rules.get("sargable_column")
    if col:
        for where in tree.find_all(exp.Where):
            for f in where.find_all(exp.Func):
                if isinstance(f, (exp.Connector, exp.Not)):
                    continue
                if any(c.name.lower() == col for c in f.find_all(exp.Column)):
                    msgs.append(f"Kolom {col} masih dibungkus fungsi di WHERE ({f.sql(dialect='duckdb')[:60]}). "
                                "Filter seperti ini tidak sargable. Bandingkan kolom langsung dengan rentang tanggal.")
                    break
            else:
                continue
            break

    if rules.get("no_func_in_join"):
        for j in tree.find_all(exp.Join):
            on = j.args.get("on")
            if not on:
                continue
            for f in on.find_all(exp.Func):
                if isinstance(f, (exp.Connector, exp.Not)):
                    continue
                if f.find(exp.Column):
                    msgs.append(f"Ada fungsi di kondisi JOIN ON ({f.sql(dialect='duckdb')[:60]}). "
                                "Fungsi di join key menghalangi pemakaian index/statistik; bersihkan datanya di hulu.")
                    break
            else:
                continue
            break
    return msgs
