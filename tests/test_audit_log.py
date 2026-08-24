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
