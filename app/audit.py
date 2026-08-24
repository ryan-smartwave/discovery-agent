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
