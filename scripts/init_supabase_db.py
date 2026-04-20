import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"), override=False)
except Exception:
    pass

from urllib.parse import urlsplit, urlunsplit

from app.core.database import get_database_url, init_db, init_engine


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
    if not url or url.startswith("sqlite:///"):
        raise SystemExit("DATABASE_URL não configurado para Postgres/Supabase.")

    engine = init_engine()
    init_db()
    print(f"OK: schema aplicado em {engine.dialect.name} -> {redact_url(url)}")


if __name__ == "__main__":
    main()
