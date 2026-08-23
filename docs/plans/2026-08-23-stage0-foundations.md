# Stage 0 — Foundations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repo scaffold + Postgres schema v1 + append-only audit log + anonymous resumable sessions + deletion-cascade skeleton, all test-covered and green in CI.

**Architecture:** One FastAPI app (`create_app()` factory), SQLAlchemy 2.0 ORM over PostgreSQL, Alembic migrations, signed httpOnly cookies for anonymous client sessions. Tests run against a **hermetic ephemeral Postgres** launched from locally installed PG 16 binaries (no Docker on the dev machine); CI uses a `postgres:16` service via `TEST_DATABASE_URL`.

**Tech Stack:** Python 3.12 · FastAPI · SQLAlchemy 2.0 + psycopg 3 · Alembic · pydantic-settings · itsdangerous · pytest + httpx · ruff · GitHub Actions.

**Spec:** [v0 build order — Stage 0](2026-08-23-v0-build-order.md) · [Architecture §9 data model, §11 security](../discovery-agent-architecture.md) · Issues [#67](https://github.com/ryan-smartwave/discovery-agent/issues/67) (audit), groundwork for [#11](https://github.com/ryan-smartwave/discovery-agent/issues/11), [#68](https://github.com/ryan-smartwave/discovery-agent/issues/68)

## Global Constraints

- `audit_log` is **append-only**: UPDATE/DELETE must fail at the database level (trigger), not just by convention (US-10.4).
- `audit_log.session_id` is a plain UUID column, **not** a foreign key — deleting a session must NOT delete its audit rows (US-10.5: legally-retained records survive deletion).
- All other per-session tables cascade on session delete (`ON DELETE CASCADE`).
- `intake.stated_problem` is `TEXT NOT NULL` — stored verbatim; no code path may rewrite it (PRD §4 Phase 0).
- Client sessions are anonymous: signed httpOnly cookie, no accounts (US-1.1).
- Env vars are prefixed `DA_` (e.g. `DA_DATABASE_URL`, `DA_SECRET_KEY`).
- Dev machine facts: Python 3.12.2 at `python`; PG binaries at `C:\Program Files\PostgreSQL\16\bin` (override with `PG_BIN`); no Docker locally — never require Docker for tests.
- Work on branch `stage0-foundations`; conventional-commit messages.

## File structure

```
discovery-agent/
├── pyproject.toml              # project metadata, deps, ruff+pytest config
├── Dockerfile                  # deploy image (used by compose/CI later, not local dev)
├── docker-compose.yml          # web + postgres + redis (VM deploy path)
├── .github/workflows/ci.yml    # ruff + pytest on push/PR
├── alembic.ini
├── migrations/
│   ├── env.py
│   └── versions/0001_schema_v1.py
├── app/
│   ├── __init__.py
│   ├── config.py               # Settings (pydantic-settings, DA_ prefix)
│   ├── db.py                   # Base, make_engine, get_db dependency
│   ├── models.py               # schema v1 ORM tables
│   ├── audit.py                # record_event()
│   ├── main.py                 # create_app(), /healthz
│   └── routes/
│       ├── __init__.py
│       └── sessions.py         # POST /sessions, GET /sessions/current, DELETE /sessions/{id}
└── tests/
    ├── conftest.py             # ephemeral PG, migrations, app/client fixtures
    ├── test_health.py
    ├── test_migrations.py
    ├── test_audit_log.py
    ├── test_sessions.py
    └── test_deletion.py
```

---

### Task 1: Project scaffold, app factory, health endpoint

**Files:**
- Create: `pyproject.toml`, `app/__init__.py`, `app/config.py`, `app/main.py`, `tests/test_health.py`, `tests/__init__.py` (empty)

**Interfaces:**
- Produces: `app.main.create_app() -> fastapi.FastAPI` (later tasks add routers/state to it); `app.config.Settings` with fields `database_url: str`, `secret_key: str`, loaded from env prefix `DA_`.

- [ ] **Step 1: Create branch**

```bash
git checkout -b stage0-foundations
```

- [ ] **Step 2: Write `pyproject.toml`**

```toml
[project]
name = "discovery-agent"
version = "0.0.1"
description = "AI-led discovery interview -> human-reviewed proposal"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "sqlalchemy>=2.0.30",
    "psycopg[binary]>=3.2",
    "alembic>=1.13",
    "pydantic>=2.8",
    "pydantic-settings>=2.4",
    "itsdangerous>=2.2",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.2",
    "pytest-timeout>=2.3",
    "httpx>=0.27",
    "ruff>=0.6",
]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = ["app", "app.routes"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.pytest.ini_options]
testpaths = ["tests"]
timeout = 120
```

- [ ] **Step 3: Write the failing test**

`tests/test_health.py`:

```python
from fastapi.testclient import TestClient

from app.main import create_app


def test_healthz_returns_ok():
    client = TestClient(create_app())
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
```

- [ ] **Step 4: Install and verify the test fails**

```bash
python -m pip install -e .[dev]
python -m pytest tests/test_health.py -v
```

Expected: FAIL (ModuleNotFoundError: app.main / create_app not defined).

- [ ] **Step 5: Implement config and app factory**

`app/__init__.py`: empty file.

`app/config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DA_")

    database_url: str = "postgresql+psycopg://postgres@127.0.0.1:5432/discovery"
    secret_key: str = "dev-only-not-a-secret"


def get_settings() -> Settings:
    return Settings()
```

`app/main.py`:

```python
from fastapi import FastAPI

from app.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Discovery Agent")
    app.state.settings = settings

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    return app
```

- [ ] **Step 6: Run test to verify it passes**

```bash
python -m pytest tests/test_health.py -v
```

Expected: PASS.

- [ ] **Step 7: Lint and commit**

```bash
python -m ruff check .
git add pyproject.toml app tests
git commit -m "feat: project scaffold with app factory and health endpoint"
```

---

### Task 2: Ephemeral Postgres test fixture + db module

**Files:**
- Create: `app/db.py`, `tests/conftest.py`, `tests/test_conftest_pg.py`

**Interfaces:**
- Consumes: `app.config.Settings`.
- Produces: `app.db.Base` (DeclarativeBase), `app.db.make_engine(url: str) -> Engine`, `app.db.SessionLocal(engine) -> sessionmaker`; pytest fixtures `pg_url` (session-scoped str), `engine` (session-scoped Engine). Later tasks add `migrated` and `db`/`client` fixtures to the same conftest.

- [ ] **Step 1: Write the failing test**

`tests/test_conftest_pg.py`:

```python
from sqlalchemy import text


def test_ephemeral_postgres_answers(engine):
    with engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1
        version = conn.execute(text("SHOW server_version")).scalar()
        assert int(version.split(".")[0]) >= 16
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_conftest_pg.py -v
```

Expected: FAIL (fixture 'engine' not found).

- [ ] **Step 3: Implement db module**

`app/db.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def make_engine(url: str) -> Engine:
    return create_engine(url, pool_pre_ping=True)


def SessionLocal(engine: Engine) -> sessionmaker:
    return sessionmaker(bind=engine, expire_on_commit=False)
```

- [ ] **Step 4: Implement the ephemeral-PG fixture**

`tests/conftest.py`:

```python
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
    subprocess.run(
        [pg_ctl, "-D", str(data), "-w", "-l", str(tmp / "pg.log"),
         "-o", f'-p {port} -c listen_addresses=127.0.0.1', "start"],
        check=True, capture_output=True,
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
```

- [ ] **Step 5: Run test to verify it passes**

```bash
python -m pytest tests/test_conftest_pg.py -v
```

Expected: PASS (first run pays ~5–10s for initdb).

- [ ] **Step 6: Lint and commit**

```bash
python -m ruff check .
git add app/db.py tests
git commit -m "feat: db engine module and hermetic ephemeral-postgres test fixture"
```

---

### Task 3: Schema v1 — ORM models + Alembic migration

**Files:**
- Create: `app/models.py`, `alembic.ini`, `migrations/env.py`, `migrations/versions/0001_schema_v1.py`, `tests/test_migrations.py`
- Modify: `tests/conftest.py` (add `migrated` + `db` fixtures)

**Interfaces:**
- Consumes: `app.db.Base`, fixtures from Task 2.
- Produces: ORM classes `Session`, `Intake`, `ProblemFrame`, `Consent`, `Message`, `Figure`, `WarStory`, `Coverage`, `Finding`, `GateResult`, `Document`, `AuditLog` in `app.models`; fixtures `migrated` (session-scoped, runs `alembic upgrade head`) and `db` (function-scoped SQLAlchemy session with per-test truncation).

- [ ] **Step 1: Write the failing test**

`tests/test_migrations.py`:

```python
from sqlalchemy import inspect

EXPECTED_TABLES = {
    "sessions", "intake", "problem_frames", "consents", "messages",
    "figures", "war_stories", "coverage", "findings", "gate_results",
    "documents", "audit_log",
}


def test_migration_creates_schema_v1(migrated, engine):
    tables = set(inspect(engine).get_table_names())
    missing = EXPECTED_TABLES - tables
    assert not missing, f"missing tables: {missing}"


def test_stated_problem_is_not_nullable(migrated, engine):
    cols = {c["name"]: c for c in inspect(engine).get_columns("intake")}
    assert cols["stated_problem"]["nullable"] is False


def test_audit_log_session_id_has_no_foreign_key(migrated, engine):
    fks = inspect(engine).get_foreign_keys("audit_log")
    assert fks == []
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_migrations.py -v
```

Expected: FAIL (fixture 'migrated' not found).

- [ ] **Step 3: Write the ORM models**

`app/models.py`:

```python
import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, DateTime, Float, ForeignKey,
    Integer, Numeric, Text, func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def _uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def _session_fk() -> Mapped[uuid.UUID]:
    return mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )


class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[uuid.UUID] = _uuid_pk()
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False)
    phase: Mapped[str] = mapped_column(Text, nullable=False, default="intake")
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    lang_profile: Mapped[dict | None] = mapped_column(JSONB)
    token_spend: Mapped[dict | None] = mapped_column(JSONB)


class Intake(Base):
    __tablename__ = "intake"
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"),
        primary_key=True)
    business_name: Mapped[str | None] = mapped_column(Text)
    business_desc: Mapped[str | None] = mapped_column(Text)
    stated_problem: Mapped[str] = mapped_column(Text, nullable=False)  # verbatim
    role: Mapped[str | None] = mapped_column(Text)
    size_band: Mapped[str | None] = mapped_column(Text)
    customer_type: Mapped[str | None] = mapped_column(Text)


class ProblemFrame(Base):
    __tablename__ = "problem_frames"
    id: Mapped[uuid.UUID] = _uuid_pk()
    session_id: Mapped[uuid.UUID] = _session_fk()
    classes: Mapped[dict] = mapped_column(JSONB, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    sidedness: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    private_individuals: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    pain_hypothesis: Mapped[str | None] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class Consent(Base):
    __tablename__ = "consents"
    id: Mapped[uuid.UUID] = _uuid_pk()
    session_id: Mapped[uuid.UUID] = _session_fk()
    text_version: Mapped[str] = mapped_column(Text, nullable=False)
    accepted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False)
    ip_hash: Mapped[str | None] = mapped_column(Text)


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (CheckConstraint("sender IN ('client','agent')", name="ck_sender"),)
    id: Mapped[uuid.UUID] = _uuid_pk()
    session_id: Mapped[uuid.UUID] = _session_fk()
    sender: Mapped[str] = mapped_column(Text, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    audio_object_key: Mapped[str | None] = mapped_column(Text)
    transcript_confidence: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False)


class Figure(Base):
    __tablename__ = "figures"
    __table_args__ = (CheckConstraint(
        "provenance IN ('user_stated','suggested_range','computed')", name="ck_provenance"),)
    id: Mapped[uuid.UUID] = _uuid_pk()
    session_id: Mapped[uuid.UUID] = _session_fk()
    name: Mapped[str] = mapped_column(Text, nullable=False)
    value_low: Mapped[float] = mapped_column(Numeric, nullable=False)
    value_high: Mapped[float] = mapped_column(Numeric, nullable=False)
    unit: Mapped[str] = mapped_column(Text, nullable=False)
    provenance: Mapped[str] = mapped_column(Text, nullable=False)
    source_msg_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("messages.id", ondelete="SET NULL"))


class WarStory(Base):
    __tablename__ = "war_stories"
    id: Mapped[uuid.UUID] = _uuid_pk()
    session_id: Mapped[uuid.UUID] = _session_fk()
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    consequence: Mapped[str | None] = mapped_column(Text)
    priced_cost: Mapped[float | None] = mapped_column(Numeric)
    source_msg_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("messages.id", ondelete="SET NULL"))


class Coverage(Base):
    __tablename__ = "coverage"
    __table_args__ = (CheckConstraint(
        "status IN ('pending','active','covered','parked')", name="ck_coverage_status"),)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"),
        primary_key=True)
    dimension: Mapped[str] = mapped_column(Text, primary_key=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")
    q_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Finding(Base):
    __tablename__ = "findings"
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"),
        primary_key=True)
    dimension: Mapped[str] = mapped_column(Text, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    corrected_from: Mapped[str | None] = mapped_column(Text)


class GateResult(Base):
    __tablename__ = "gate_results"
    __table_args__ = (CheckConstraint(
        "classification IN ('now','later')", name="ck_classification"),)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"),
        primary_key=True)
    g1: Mapped[bool] = mapped_column(Boolean, nullable=False)
    g2: Mapped[bool] = mapped_column(Boolean, nullable=False)
    g3: Mapped[bool] = mapped_column(Boolean, nullable=False)
    g4: Mapped[bool] = mapped_column(Boolean, nullable=False)
    classification: Mapped[str] = mapped_column(Text, nullable=False)
    failed_reason: Mapped[str | None] = mapped_column(Text)
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False)


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint("kind IN ('proposal','later_memo')", name="ck_doc_kind"),
        CheckConstraint("status IN ('draft','approved','sent')", name="ck_doc_status"),
    )
    id: Mapped[uuid.UUID] = _uuid_pk()
    session_id: Mapped[uuid.UUID] = _session_fk()
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    md_key: Mapped[str | None] = mapped_column(Text)
    pdf_key: Mapped[str | None] = mapped_column(Text)
    docx_key: Mapped[str | None] = mapped_column(Text)
    config_version: Mapped[str | None] = mapped_column(Text)
    checks: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="draft")
    approved_by: Mapped[str | None] = mapped_column(Text)


class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    # Deliberately NOT a ForeignKey: audit rows must survive session deletion.
    session_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), index=True)
    actor: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False)
```

- [ ] **Step 4: Set up Alembic**

`alembic.ini`:

```ini
[alembic]
script_location = migrations
sqlalchemy.url =

[loggers]
keys = root

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
```

`migrations/env.py`:

```python
import os

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.db import Base
from app import models  # noqa: F401  (registers tables on Base.metadata)

config = context.config
url = os.environ.get("DA_DATABASE_URL") or config.get_main_option("sqlalchemy.url")
config.set_main_option("sqlalchemy.url", url)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

`migrations/versions/0001_schema_v1.py` (hand-written; uses metadata create_all — acceptable for the v0 spike where migration 0001 IS the model definition; later migrations use explicit ops):

```python
"""schema v1

Revision ID: 0001
Revises:
Create Date: 2026-08-23
"""
from alembic import op

from app.db import Base
from app import models  # noqa: F401

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
```

- [ ] **Step 5: Add `migrated` and `db` fixtures**

Append to `tests/conftest.py`:

```python
from alembic import command
from alembic.config import Config
from sqlalchemy import text

from app.db import SessionLocal


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
```

(`TRUNCATE sessions ... CASCADE` clears every child table via FKs; `audit_log` is truncated explicitly because it has no FK. The trigger toggle exists because Task 4 makes audit_log delete-proof; TRUNCATE is blocked by the same trigger family only if written as row-level — see Task 4, which must also add a truncate-blocking statement trigger, hence the explicit disable/enable here.)

- [ ] **Step 6: Run tests to verify they pass**

```bash
python -m pytest tests/test_migrations.py -v
```

Expected: 3 PASS.

- [ ] **Step 7: Full suite, lint, commit**

```bash
python -m pytest -v
python -m ruff check .
git add app/models.py alembic.ini migrations tests/conftest.py tests/test_migrations.py
git commit -m "feat: schema v1 ORM models and alembic migration"
```

---

### Task 4: Append-only audit log + `record_event()`

**Files:**
- Create: `app/audit.py`, `tests/test_audit_log.py`
- Modify: `migrations/versions/0001_schema_v1.py` (add trigger DDL to upgrade)

**Interfaces:**
- Consumes: `app.models.AuditLog`, `db` fixture.
- Produces: `app.audit.record_event(db, *, session_id: uuid.UUID | None, actor: str, event_type: str, payload: dict | None = None) -> None` (flushes, does not commit — caller owns the transaction). Every later component calls this.

- [ ] **Step 1: Write the failing tests**

`tests/test_audit_log.py`:

```python
import uuid

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError

from app.audit import record_event
from app.models import AuditLog, Session


def _make_session(db):
    s = Session()
    db.add(s)
    db.flush()
    return s


def test_record_event_appends_row(db):
    s = _make_session(db)
    record_event(db, session_id=s.id, actor="system",
                 event_type="session.created", payload={"phase": "intake"})
    db.commit()
    rows = db.execute(select(AuditLog)).scalars().all()
    assert len(rows) == 1
    assert rows[0].event_type == "session.created"
    assert rows[0].payload == {"phase": "intake"}


def test_audit_rows_cannot_be_updated(db):
    record_event(db, session_id=None, actor="system", event_type="x")
    db.commit()
    with pytest.raises(DBAPIError, match="append-only"):
        db.execute(text("UPDATE audit_log SET actor = 'evil'"))
        db.commit()
    db.rollback()


def test_audit_rows_cannot_be_deleted(db):
    record_event(db, session_id=None, actor="system", event_type="x")
    db.commit()
    with pytest.raises(DBAPIError, match="append-only"):
        db.execute(text("DELETE FROM audit_log"))
        db.commit()
    db.rollback()


def test_audit_rows_survive_session_deletion(db):
    s = _make_session(db)
    record_event(db, session_id=s.id, actor="system", event_type="session.created")
    db.commit()
    db.delete(s)
    db.commit()
    remaining = db.execute(
        select(AuditLog).where(AuditLog.session_id == s.id)).scalars().all()
    assert len(remaining) == 1


def test_record_event_rejects_unknown_uuid_types():
    with pytest.raises(TypeError):
        record_event(None, session_id="not-a-uuid", actor="system", event_type="x")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_audit_log.py -v
```

Expected: FAIL (no module app.audit; update/delete tests fail once module exists but trigger doesn't).

- [ ] **Step 3: Add trigger DDL to migration 0001**

In `migrations/versions/0001_schema_v1.py`, extend `upgrade()` after `create_all`:

```python
AUDIT_TRIGGER_SQL = """
CREATE OR REPLACE FUNCTION audit_log_immutable() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'audit_log is append-only';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_log_no_mutate
    BEFORE UPDATE OR DELETE ON audit_log
    FOR EACH ROW EXECUTE FUNCTION audit_log_immutable();
"""


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())
    op.execute(AUDIT_TRIGGER_SQL)
```

(No statement-level TRUNCATE trigger: TRUNCATE requires table ownership and is not exposed through any app code path; the conftest truncation between tests uses `DISABLE TRIGGER USER` as superuser. Add `op.execute("DROP FUNCTION IF EXISTS audit_log_immutable CASCADE")` to `downgrade()` before `drop_all`.)

- [ ] **Step 4: Implement `record_event`**

`app/audit.py`:

```python
import uuid

from sqlalchemy import insert
from sqlalchemy.orm import Session as OrmSession

from app.models import AuditLog


def record_event(
    db: OrmSession,
    *,
    session_id: uuid.UUID | None,
    actor: str,
    event_type: str,
    payload: dict | None = None,
) -> None:
    """Append one audit event. Flushes; the caller owns commit/rollback."""
    if session_id is not None and not isinstance(session_id, uuid.UUID):
        raise TypeError("session_id must be a uuid.UUID or None")
    db.execute(insert(AuditLog).values(
        session_id=session_id, actor=actor, event_type=event_type, payload=payload))
    db.flush()
```

- [ ] **Step 5: Rebuild the test database and run tests**

The migration changed, and `migrated` is session-scoped — a stale ephemeral cluster does not exist between runs (fresh initdb each session), so simply:

```bash
python -m pytest tests/test_audit_log.py -v
```

Expected: 5 PASS.

- [ ] **Step 6: Full suite, lint, commit**

```bash
python -m pytest -v
python -m ruff check .
git add app/audit.py migrations tests/test_audit_log.py
git commit -m "feat: append-only audit log with db-level immutability trigger"
```

---

### Task 5: Anonymous session issuance + resume (signed cookie)

**Files:**
- Create: `app/routes/__init__.py` (empty), `app/routes/sessions.py`, `tests/test_sessions.py`
- Modify: `app/main.py` (wire engine + router), `tests/conftest.py` (add `client` fixture)

**Interfaces:**
- Consumes: `create_app()`, `record_event`, models, `db` fixture.
- Produces: HTTP API — `POST /sessions` → 201 `{"session_id": "<uuid>"}` + `Set-Cookie: da_session=<signed>; HttpOnly; SameSite=Lax; Path=/`; `GET /sessions/current` → 200 `{"session_id", "phase", "status"}` or 401 `{"detail": "no session"}`. Internal: `app.routes.sessions.sign_session_id(secret: str, session_id: str) -> str` and `unsign_session_id(secret: str, value: str) -> str | None`; FastAPI dependency `get_db` yielding an ORM session from `app.state.engine`; cookie name constant `SESSION_COOKIE = "da_session"`.

- [ ] **Step 1: Write the failing tests**

`tests/test_sessions.py`:

```python
import uuid

from sqlalchemy import select

from app.models import AuditLog, Session
from app.routes.sessions import SESSION_COOKIE, sign_session_id


def test_create_session_sets_signed_cookie_and_persists(client, db):
    resp = client.post("/sessions")
    assert resp.status_code == 201
    sid = resp.json()["session_id"]
    uuid.UUID(sid)  # valid uuid
    assert SESSION_COOKIE in resp.cookies
    assert resp.cookies[SESSION_COOKIE] != sid  # signed, not raw
    row = db.get(Session, uuid.UUID(sid))
    assert row is not None and row.status == "active" and row.phase == "intake"
    events = db.execute(select(AuditLog).where(
        AuditLog.session_id == uuid.UUID(sid))).scalars().all()
    assert any(e.event_type == "session.created" for e in events)


def test_resume_with_cookie(client):
    created = client.post("/sessions").json()["session_id"]
    resp = client.get("/sessions/current")
    assert resp.status_code == 200
    body = resp.json()
    assert body["session_id"] == created
    assert body["phase"] == "intake"
    assert body["status"] == "active"


def test_current_without_cookie_is_401(client):
    client.cookies.clear()
    assert client.get("/sessions/current").status_code == 401


def test_current_with_tampered_cookie_is_401(client):
    client.post("/sessions")
    client.cookies.set(SESSION_COOKIE, "forged-value")
    assert client.get("/sessions/current").status_code == 401


def test_cookie_signed_with_wrong_key_is_rejected(client):
    sid = client.post("/sessions").json()["session_id"]
    client.cookies.set(SESSION_COOKIE, sign_session_id("wrong-key", sid))
    assert client.get("/sessions/current").status_code == 401
```

- [ ] **Step 2: Add the `client` fixture**

Append to `tests/conftest.py`:

```python
from fastapi.testclient import TestClient


@pytest.fixture()
def client(pg_url, migrated, monkeypatch, db):
    monkeypatch.setenv("DA_DATABASE_URL", pg_url)
    monkeypatch.setenv("DA_SECRET_KEY", "test-secret-key")
    from app.main import create_app
    app = create_app()
    with TestClient(app) as c:
        yield c
```

(The `db` parameter is deliberate even when unused by a test: it guarantees post-test truncation runs.)

- [ ] **Step 3: Run tests to verify they fail**

```bash
python -m pytest tests/test_sessions.py -v
```

Expected: FAIL (no app.routes.sessions).

- [ ] **Step 4: Implement the sessions router**

`app/routes/sessions.py`:

```python
import uuid
from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from itsdangerous import BadSignature, URLSafeSerializer
from sqlalchemy.orm import Session as OrmSession

from app.audit import record_event
from app.db import SessionLocal
from app.models import Session as SessionRow

SESSION_COOKIE = "da_session"
router = APIRouter()


def sign_session_id(secret: str, session_id: str) -> str:
    return URLSafeSerializer(secret, salt="da-session").dumps(session_id)


def unsign_session_id(secret: str, value: str) -> str | None:
    try:
        return URLSafeSerializer(secret, salt="da-session").loads(value)
    except BadSignature:
        return None


def get_db(request: Request) -> Iterator[OrmSession]:
    db = SessionLocal(request.app.state.engine)()
    try:
        yield db
    finally:
        db.close()


def current_session_id(request: Request) -> uuid.UUID:
    raw = request.cookies.get(SESSION_COOKIE)
    if raw is None:
        raise HTTPException(status_code=401, detail="no session")
    sid = unsign_session_id(request.app.state.settings.secret_key, raw)
    if sid is None:
        raise HTTPException(status_code=401, detail="no session")
    return uuid.UUID(sid)


@router.post("/sessions", status_code=201)
def create_session(request: Request, response: Response,
                   db: OrmSession = Depends(get_db)) -> dict[str, str]:
    row = SessionRow()
    db.add(row)
    db.flush()
    record_event(db, session_id=row.id, actor="system",
                 event_type="session.created", payload={"phase": row.phase})
    db.commit()
    signed = sign_session_id(request.app.state.settings.secret_key, str(row.id))
    response.set_cookie(SESSION_COOKIE, signed, httponly=True, samesite="lax", path="/")
    return {"session_id": str(row.id)}


@router.get("/sessions/current")
def get_current(request: Request, db: OrmSession = Depends(get_db)) -> dict[str, str]:
    sid = current_session_id(request)
    row = db.get(SessionRow, sid)
    if row is None:
        raise HTTPException(status_code=401, detail="no session")
    return {"session_id": str(row.id), "phase": row.phase, "status": row.status}
```

- [ ] **Step 5: Wire engine and router into the app factory**

`app/main.py` becomes:

```python
from fastapi import FastAPI

from app.config import get_settings
from app.db import make_engine
from app.routes.sessions import router as sessions_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Discovery Agent")
    app.state.settings = settings
    app.state.engine = make_engine(settings.database_url)

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(sessions_router)
    return app
```

Also update `tests/test_health.py` — `create_app()` now builds an engine, so the health test must set env first:

```python
def test_healthz_returns_ok(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
python -m pytest tests/test_sessions.py tests/test_health.py -v
```

Expected: all PASS.

- [ ] **Step 7: Full suite, lint, commit**

```bash
python -m pytest -v
python -m ruff check .
git add app tests
git commit -m "feat: anonymous resumable sessions with signed httpOnly cookie"
```

---

### Task 6: Deletion-cascade skeleton

**Files:**
- Modify: `app/routes/sessions.py` (add DELETE endpoint)
- Create: `tests/test_deletion.py`

**Interfaces:**
- Consumes: everything above.
- Produces: `DELETE /sessions/{session_id}` → 204 (own session only; cookie must match path id, else 403; unknown id → 404). Cascades all child rows; audit rows survive; a final `session.deleted` audit event is written; cookie cleared.

- [ ] **Step 1: Write the failing tests**

`tests/test_deletion.py`:

```python
import uuid

from sqlalchemy import func, select

from app.models import AuditLog, Consent, Figure, Intake, Message, Session


def _populate(db, sid: uuid.UUID):
    db.add(Intake(session_id=sid, stated_problem="walang customers"))
    db.add(Consent(session_id=sid, text_version="v1"))
    msg = Message(session_id=sid, sender="client", text="10 to 15 hours siguro")
    db.add(msg)
    db.flush()
    db.add(Figure(session_id=sid, name="hours_per_month", value_low=10,
                  value_high=15, unit="hours", provenance="user_stated",
                  source_msg_id=msg.id))
    db.commit()


def test_delete_cascades_children_and_keeps_audit(client, db):
    sid = uuid.UUID(client.post("/sessions").json()["session_id"])
    _populate(db, sid)

    resp = client.delete(f"/sessions/{sid}")
    assert resp.status_code == 204

    assert db.get(Session, sid) is None
    for model in (Intake, Consent, Message, Figure):
        count = db.execute(select(func.count()).select_from(model)).scalar()
        assert count == 0, f"{model.__tablename__} not cascaded"

    events = db.execute(select(AuditLog.event_type).where(
        AuditLog.session_id == sid)).scalars().all()
    assert "session.created" in events
    assert "session.deleted" in events


def test_cannot_delete_someone_elses_session(client, db):
    other = Session()
    db.add(other)
    db.commit()
    client.post("/sessions")  # my own cookie
    resp = client.delete(f"/sessions/{other.id}")
    assert resp.status_code == 403
    assert db.get(Session, other.id) is not None


def test_delete_unknown_session_is_404(client):
    sid = client.post("/sessions").json()["session_id"]
    client.delete(f"/sessions/{sid}")
    assert client.delete(f"/sessions/{sid}").status_code == 404
```

(Note: the second `delete` in the 404 test runs with a now-dangling cookie — the endpoint must check existence *after* the ownership check passes, since cookie id == path id.)

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_deletion.py -v
```

Expected: FAIL (405 Method Not Allowed).

- [ ] **Step 3: Implement the endpoint**

Append to `app/routes/sessions.py`:

```python
@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: uuid.UUID, request: Request, response: Response,
                   db: OrmSession = Depends(get_db)) -> Response:
    sid = current_session_id(request)
    if sid != session_id:
        raise HTTPException(status_code=403, detail="not your session")
    row = db.get(SessionRow, session_id)
    if row is None:
        raise HTTPException(status_code=404, detail="unknown session")
    db.delete(row)  # FK cascades clear all child tables
    record_event(db, session_id=session_id, actor="client",
                 event_type="session.deleted")
    db.commit()
    response = Response(status_code=204)
    response.delete_cookie(SESSION_COOKIE, path="/")
    return response
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_deletion.py -v
```

Expected: 3 PASS.

- [ ] **Step 5: Full suite, lint, commit**

```bash
python -m pytest -v
python -m ruff check .
git add app/routes/sessions.py tests/test_deletion.py
git commit -m "feat: session deletion with FK cascade, audit retention, ownership check"
```

---

### Task 7: Deploy artifacts + CI

**Files:**
- Create: `Dockerfile`, `docker-compose.yml`, `.github/workflows/ci.yml`, `.dockerignore`

**Interfaces:**
- Consumes: the finished app.
- Produces: CI green on GitHub Actions for every push/PR; `docker compose up` topology for the future VM deploy (not runnable on this dev machine — no Docker — and that is fine).

- [ ] **Step 1: Write the deploy files**

`Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /srv
COPY pyproject.toml ./
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000"]
```

`.dockerignore`:

```
.git
tests
docs
__pycache__
*.pyc
```

`docker-compose.yml`:

```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      DA_DATABASE_URL: postgresql+psycopg://postgres:postgres@postgres:5432/discovery
      DA_SECRET_KEY: ${DA_SECRET_KEY:?set DA_SECRET_KEY in .env}
    depends_on:
      postgres:
        condition: service_healthy
  postgres:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: discovery
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 10
  redis:
    image: redis:7
volumes:
  pgdata:
```

`.github/workflows/ci.yml`:

```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U postgres"
          --health-interval 5s --health-timeout 3s --health-retries 10
    env:
      TEST_DATABASE_URL: postgresql+psycopg://postgres:postgres@localhost:5432/postgres
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install -e .[dev]
      - run: python -m ruff check .
      - run: python -m pytest -v
```

- [ ] **Step 2: Run the full local suite one more time**

```bash
python -m pytest -v
python -m ruff check .
```

Expected: all PASS, no lint errors.

- [ ] **Step 3: Commit**

```bash
git add Dockerfile .dockerignore docker-compose.yml .github
git commit -m "chore: deploy artifacts (Dockerfile, compose) and GitHub Actions CI"
```

- [ ] **Step 4: Push branch and verify CI**

```bash
git push -u origin stage0-foundations
```

Then watch the Actions run for the branch; expected green. (Merging to main happens after review — see finishing-a-development-branch.)

---

## Stage exit criteria (from the build order)

- [ ] Full test suite green locally against ephemeral PG 16 and in CI against postgres:16.
- [ ] Migration applies from zero (proved by every test session).
- [ ] Audit rows provably immutable at the DB level and survive session deletion.
- [ ] Sessions issue/resume via signed httpOnly cookie; tampered or foreign cookies rejected.
- [ ] Closing note on issue [#67](https://github.com/ryan-smartwave/discovery-agent/issues/67) (infrastructure half done; verification half returns in Stage 7).
