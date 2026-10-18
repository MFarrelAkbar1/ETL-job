"""Cek apakah Java 17+ tersedia untuk Modul 5 (PySpark). Tidak pernah membuat setup gagal."""

import re
import shutil
import subprocess


def java_major() -> int | None:
    if not shutil.which("java"):
        return None
    out = subprocess.run(["java", "-version"], capture_output=True, text=True)
    m = re.search(r'version "(\d+)(?:\.(\d+))?', out.stderr + out.stdout)
    if not m:
        return None
    major = int(m.group(1))
    return int(m.group(2)) if major == 1 and m.group(2) else major


if __name__ == "__main__":
    v = java_major()
    if v is not None and v >= 17:
        print(f"Java {v} terdeteksi: Modul 5 (PySpark) bisa diaktifkan.")
    else:
        found = f"Java {v}" if v else "Java tidak ditemukan"
        print(f"{found}. Modul 5 (PySpark) dilewati. Lihat README bagian 'Install Java 17'.")
