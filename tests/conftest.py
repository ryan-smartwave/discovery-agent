import os
import shutil
import socket
import subprocess
import tempfile
from pathlib import Path

import pytest

from app.db import make_engine

DEFAULT_PG_BIN = r"C:\Program Files\PostgreSQL\16\bin"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def pg_url():
    """Hermetic Postgres: TEST_DATABASE_URL if set (CI), else ephemeral initdb."""
    external = os.environ.get("TEST_DATABASE_URL")
    if external:
        yield external
        return

    pg_bin = Path(os.environ.get("PG_BIN", DEFAULT_PG_BIN))
    initdb, pg_ctl = str(pg_bin / "initdb"), str(pg_bin / "pg_ctl")
    tmp = Path(tempfile.mkdtemp(prefix="dapg_"))
    data = tmp / "data"
    subprocess.run(
        [initdb, "-D", str(data), "-U", "postgres", "-A", "trust", "-E", "UTF8"],
        check=True, capture_output=True,
    )
    port = _free_port()
    # stdout/stderr must NOT be piped here: pg_ctl's grandchild postgres.exe
    # inherits those handles on Windows and keeps them open past pg_ctl's own
    # exit, so a captured pipe read blocks forever. -l already logs to file.
    subprocess.run(
        [pg_ctl, "-D", str(data), "-w", "-l", str(tmp / "pg.log"),
         "-o", f'-p {port} -c listen_addresses=127.0.0.1', "start"],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        yield f"postgresql+psycopg://postgres@127.0.0.1:{port}/postgres"
    finally:
        subprocess.run([pg_ctl, "-D", str(data), "-m", "immediate", "stop"],
                       check=True, capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture(scope="session")
def engine(pg_url):
    eng = make_engine(pg_url)
    yield eng
    eng.dispose()
