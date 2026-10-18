import logging

import pytest

from py_check import check, expect_raises

EX, FILE = "p10", "p10_logging_retry"


class Flaky:
    def __init__(self, ex, fail_times, exc=None):
        self.ex, self.fail_times, self.calls, self.exc = ex, fail_times, 0, exc

    def __call__(self):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise self.exc or self.ex.TransientError(f"timeout ke-{self.calls}")
        return "OK"


@pytest.fixture
def logger():
    lg = logging.getLogger("test_retry")
    lg.setLevel(logging.DEBUG)
    return lg


def test_sukses_setelah_retry(ex, caplog, logger):
    f = Flaky(ex, 2)
    with caplog.at_level(logging.DEBUG, logger="test_retry"):
        res = ex.run_with_retry(f, retries=3, logger=logger)
    check(res == "OK", f"Hasil func harus dikembalikan, didapat {res!r}.")
    check(f.calls == 3, f"func seharusnya dipanggil 3 kali (2 gagal + 1 sukses), dipanggil {f.calls} kali.")
    warns = [r for r in caplog.records if r.levelno == logging.WARNING]
    check(len(warns) == 2, f"Harus ada 2 log WARNING, ada {len(warns)}.")
    check("percobaan 1/4" in warns[0].getMessage(), f"WARNING pertama harus memuat 'percobaan 1/4'. Isi: {warns[0].getMessage()!r}")
    check(any(r.levelno == logging.INFO for r in caplog.records), "Sukses harus dicatat dengan level INFO.")


def test_habis_percobaan(ex, caplog, logger):
    f = Flaky(ex, 99)
    with caplog.at_level(logging.DEBUG, logger="test_retry"):
        e = expect_raises(ex.TransientError, ex.run_with_retry, f, retries=2, logger=logger,
                          msg="Setelah percobaan habis, exception TransientError terakhir harus di-raise ulang.")
    check(f.calls == 3, f"retries=2 berarti total 3 percobaan, func dipanggil {f.calls} kali.")
    check("ke-3" in str(e), f"Yang di-raise harus exception TERAKHIR (timeout ke-3), didapat: {e}")
    check(any(r.levelno == logging.ERROR for r in caplog.records), "Kegagalan akhir harus dicatat ERROR.")


def test_error_lain_tidak_diretry(ex, caplog, logger):
    f = Flaky(ex, 99, exc=ValueError("data rusak"))
    with caplog.at_level(logging.DEBUG, logger="test_retry"):
        expect_raises(ValueError, ex.run_with_retry, f, retries=3, logger=logger,
                      msg="Exception non-transient harus langsung di-raise ulang.")
    check(f.calls == 1, f"Error non-transient (misalnya data rusak) tidak boleh di-retry, func dipanggil {f.calls} kali.")


def test_backoff(ex, monkeypatch, logger):
    sleeps = []
    monkeypatch.setattr("time.sleep", lambda s: sleeps.append(s))
    ex.run_with_retry(Flaky(ex, 3), retries=3, backoff_s=1.5, logger=logger)
    check(sleeps == [1.5, 3.0, 6.0], f"Durasi tunggu {sleeps}, seharusnya exponential backoff [1.5, 3.0, 6.0].")


def test_setup_logger(ex, tmp_path):
    log_file = tmp_path / "etl.log"
    lg = ex.setup_logger("etl_test_logger", log_file)
    lg2 = ex.setup_logger("etl_test_logger", log_file)
    check(lg is lg2, "Logger dengan nama sama harus objek yang sama (logging.getLogger).")
    check(len(lg.handlers) == 2, f"Logger harus punya tepat 2 handler (file + console), punya {len(lg.handlers)}. "
          "Apakah handler ditambahkan lagi setiap kali dipanggil?")
    lg.info("halo dunia")
    for h in lg.handlers:
        h.flush()
    text = log_file.read_text(encoding="utf-8")
    check(text.count("halo dunia") == 1, f"Pesan harus tertulis tepat sekali di file, tertulis {text.count('halo dunia')} kali.")
    check("| INFO | etl_test_logger | halo dunia" in text, f"Format log belum sesuai. Isi file: {text!r}")
    for h in list(lg.handlers):
        h.close()
        lg.removeHandler(h)
