from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.db import make_engine
from app.routes.sessions import router as sessions_router


def create_app() -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        yield
        # Dispose the pooled connections on shutdown; each create_app() call
        # (one per test client, one per process in prod) owns its own engine.
        app.state.engine.dispose()

    app = FastAPI(title="Discovery Agent", lifespan=lifespan)
    app.state.settings = settings
    app.state.engine = make_engine(settings.database_url)

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(sessions_router)
    return app
