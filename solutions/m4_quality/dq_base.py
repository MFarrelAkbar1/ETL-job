"""Tipe hasil pengecekan bersama untuk Modul 4. File ini SUDAH JADI, tidak perlu diubah."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CheckResult:
    check: str                 # nama pengecekan, contoh "not_null:order_id"
    passed: bool
    failed_rows: int           # jumlah baris yang melanggar
    total_rows: int            # jumlah baris yang diperiksa
    details: dict = field(default_factory=dict)

    @property
    def failure_rate(self) -> float:
        return self.failed_rows / self.total_rows if self.total_rows else 0.0

    def __str__(self) -> str:
        status = "LULUS" if self.passed else "GAGAL"
        return f"[{status}] {self.check}: {self.failed_rows}/{self.total_rows} baris bermasalah"
