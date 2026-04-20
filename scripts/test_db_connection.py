import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"), override=False)
except Exception:
    pass

from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import text

from app.core.database import get_database_url, init_engine


def redact_url(url: str) -> str:
    try:
        parts = urlsplit(url)
        netloc = parts.netloc
        if "@" in netloc:
            userinfo, hostinfo = netloc.rsplit("@", 1)
            if ":" in userinfo:
                user = userinfo.split(":", 1)[0]
                netloc = f"{user}:***@{hostinfo}"
        return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))
    except Exception:
        return "***"


def main():
    url = get_database_url()
    print(f"DB URL: {redact_url(url)}")

    engine = init_engine()
    print(f"Dialect: {engine.dialect.name}")

    with engine.connect() as conn:
        v = conn.execute(text("select 1")).scalar()
        print(f"SELECT 1 -> {v}")

        if engine.dialect.name == "postgresql":
            dbname = conn.execute(text("select current_database()")).scalar()
            now = conn.execute(text("select now()")).scalar()
            print(f"current_database(): {dbname}")
            print(f"now(): {now}")


if __name__ == "__main__":
    main()
