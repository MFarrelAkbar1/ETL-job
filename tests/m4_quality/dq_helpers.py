"""Helper pemeriksaan CheckResult."""

from py_check import check


def check_result(r, check_name, passed, failed_rows, total_rows, where=""):
    pre = f"{where}: " if where else ""
    for attr in ("check", "passed", "failed_rows", "total_rows", "details"):
        check(hasattr(r, attr), f"{pre}hasil harus berupa CheckResult (atribut '{attr}' tidak ada).")
    check(r.check == check_name, f"{pre}CheckResult.check = {r.check!r}, seharusnya {check_name!r}.")
    check(r.failed_rows == failed_rows, f"{pre}failed_rows = {r.failed_rows}, seharusnya {failed_rows}.")
    check(r.total_rows == total_rows, f"{pre}total_rows = {r.total_rows}, seharusnya {total_rows}.")
    check(bool(r.passed) is passed, f"{pre}passed = {r.passed}, seharusnya {passed}.")
