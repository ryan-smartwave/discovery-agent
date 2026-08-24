from alembic import command
from alembic.config import Config
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


def test_env_py_prefers_explicit_config_url_over_ambient_env_var(migrated, pg_url, monkeypatch):
    """An ambient DA_DATABASE_URL (e.g. a dev's local app env) must never shadow an
    explicit Config sqlalchemy.url, or pytest could silently migrate a developer's
    real database instead of the test one. Point DA_DATABASE_URL at an address nothing
    listens on; if migrations/env.py used it instead of the config URL, connecting
    would fail. The schema is already at head via `migrated`, so this upgrade is a
    no-op against the real database, but env.py still opens a connection using the
    resolved URL every run - that's what this test exercises.
    """
    monkeypatch.setenv("DA_DATABASE_URL", "postgresql+psycopg://nobody@127.0.0.1:1/nope")
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", pg_url)
    command.upgrade(cfg, "head")
