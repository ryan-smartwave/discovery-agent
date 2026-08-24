"""schema v1

Revision ID: 0001
Revises:
Create Date: 2026-08-23
"""
from alembic import op

from app import models  # noqa: F401
from app.db import Base

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

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


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS audit_log_immutable CASCADE")
    Base.metadata.drop_all(bind=op.get_bind())
