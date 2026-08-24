from sqlalchemy import text


def test_ephemeral_postgres_answers(engine):
    with engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1
        version = conn.execute(text("SHOW server_version")).scalar()
        assert int(version.split(".")[0]) >= 16
