"""Helper bersama Modul 6. File ini SUDAH JADI, tidak perlu diubah."""

from __future__ import annotations

from pathlib import Path

from pyiceberg.catalog.sql import SqlCatalog


def get_catalog(root: str | Path, name: str = "local") -> SqlCatalog:
    """SQL catalog (SQLite) dengan warehouse di root/warehouse.

    Catatan Windows: lokasi warehouse ditulis sebagai path absolut biasa (C:/Users/...),
    BUKAN URI file:///C:/... Bentuk URI diubah PyArrow menjadi '/C:/...' dan gagal, terutama
    kalau path mengandung spasi. Di Linux/WSL hasilnya path biasa seperti /home/....
    """
    root = Path(root).resolve()
    (root / "warehouse").mkdir(parents=True, exist_ok=True)
    return SqlCatalog(
        name,
        uri=f"sqlite:///{(root / 'catalog.db').as_posix()}",
        warehouse=(root / "warehouse").as_posix(),
    )
