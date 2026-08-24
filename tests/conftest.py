import os
import shutil
import socket
import subprocess
import tempfile
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db import SessionLocal, make_engine

PG_VERSIONS = ("18", "17", "16")


def _discover_pg_bin() -> Path:
    """Find the newest installed PostgreSQL bin dir (checks 18, then 17, then 16)."""
    for version in PG_VERSIONS:
        candidate = Path(rf"C:\Program Files\PostgreSQL\{version}\bin")
        if (candidate / "initdb.exe").exists():
            return candidate
    pytest.fail(
        "No PostgreSQL installation found under C:\\Program Files\\PostgreSQL\\"
        f"{{{','.join(PG_VERSIONS)}}}\\bin. Set the PG_BIN environment variable to "
        "your PostgreSQL bin directory, or set TEST_DATABASE_URL to use an external database.",
        pytrace=False,
    )


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

    pg_bin_override = os.environ.get("PG_BIN")
    pg_bin = Path(pg_bin_override) if pg_bin_override else _discover_pg_bin()
    initdb, pg_ctl = str(pg_bin / "initdb"), str(pg_bin / "pg_ctl")
    tmp = Path(tempfile.mkdtemp(prefix="dapg_"))
    data = tmp / "data"
    started = False
    try:
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
        started = True
        yield f"postgresql+psycopg://postgres@127.0.0.1:{port}/postgres"
    finally:
        if started:
            # Best-effort: a failed stop must never block the rmtree below.
            subprocess.run([pg_ctl, "-D", str(data), "-m", "immediate", "stop"],
                           check=False, capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture(scope="session")
def engine(pg_url):
    eng = make_engine(pg_url)
    yield eng
    eng.dispose()


@pytest.fixture(scope="session")
def migrated(pg_url):
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", pg_url)
    command.upgrade(cfg, "head")
    return True


@pytest.fixture()
def db(engine, migrated):
    """Function-scoped ORM session; truncates all data tables afterwards."""
    session = SessionLocal(engine)()
    try:
        yield session
        session.rollback()
    finally:
        session.close()
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE audit_log DISABLE TRIGGER USER"))
            conn.execute(text(
                "TRUNCATE sessions, audit_log RESTART IDENTITY CASCADE"))
            conn.execute(text("ALTER TABLE audit_log ENABLE TRIGGER USER"))


@pytest.fixture()
def client(pg_url, migrated, monkeypatch, db):
    monkeypatch.setenv("DA_DATABASE_URL", pg_url)
    monkeypatch.setenv("DA_SECRET_KEY", "test-secret-key")
    from app.main import create_app
    app = create_app()
    with TestClient(app) as c:
        yield c
