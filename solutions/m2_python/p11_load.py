"""Kunci jawaban P11."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd


def load_to_duckdb(df: pd.DataFrame, db_path: str | Path, table: str, mode: str = "append",
                   key: str | list[str] | None = None) -> int:
    if mode not in ("append", "replace", "upsert"):
        raise ValueError(f"mode tidak dikenal: {mode}")
    keys = [key] if isinstance(key, str) else list(key or [])
    if mode == "upsert":
        if not keys:
            raise ValueError("mode upsert membutuhkan key")
        if df.duplicated(subset=keys).any():
            raise ValueError(f"df punya key duplikat pada {keys}")

    con = duckdb.connect(str(db_path))
    try:
        con.register("src_df", df)
        con.execute("BEGIN TRANSACTION")
        exists = con.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = ?", [table]).fetchone()[0]
        if not exists:
            con.execute(f'CREATE TABLE "{table}" AS SELECT * FROM src_df LIMIT 0')
        if mode == "replace":
            con.execute(f'DELETE FROM "{table}"')
        elif mode == "upsert":
            cond = " AND ".join(f't."{k}" = s."{k}"' for k in keys)
            con.execute(f'DELETE FROM "{table}" t WHERE EXISTS (SELECT 1 FROM src_df s WHERE {cond})')
        con.execute(f'INSERT INTO "{table}" SELECT * FROM src_df')
        con.execute("COMMIT")
        return con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
    except Exception:
        con.execute("ROLLBACK")
        raise
    finally:
        con.close()
