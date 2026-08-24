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
