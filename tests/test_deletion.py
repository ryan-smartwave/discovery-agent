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
