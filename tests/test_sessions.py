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
