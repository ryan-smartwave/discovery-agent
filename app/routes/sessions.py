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
