import os
import sys
from urllib.parse import urlsplit, urlunsplit

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"), override=False)
except Exception:
    pass

from sqlalchemy import MetaData, Table, create_engine, text

from app.core.database import app_data_path, get_database_url


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


def fetch_all(conn, table: Table) -> list[dict]:
    rows = conn.execute(table.select()).mappings().all()
    return [dict(r) for r in rows]


def bulk_insert(conn, table: Table, rows: list[dict]):
    if not rows:
        return
    conn.execute(table.insert(), rows)


def set_sequence(conn, table_name: str):
    max_id = conn.execute(text(f"select max(id) from {table_name}")).scalar()
    if max_id is None:
        return
    conn.execute(
        text(
            "select setval(pg_get_serial_sequence(:t, 'id'), :v, true)"
        ),
        {"t": table_name, "v": int(max_id)},
    )


def main():
    src_sqlite = os.getenv("SQLITE_PATH") or app_data_path("database.db")
    src_url = f"sqlite:///{src_sqlite}"
    dst_url = get_database_url()
    if not dst_url or dst_url.startswith("sqlite:///"):
        raise SystemExit("Configure DATABASE_URL do Supabase no .env antes de migrar.")

    print(f"Origem: {src_url}")
    print(f"Destino: {redact_url(dst_url)}")

    src_engine = create_engine(src_url, echo=False)
    dst_engine = create_engine(dst_url, echo=False, pool_pre_ping=True)

    meta_src = MetaData()
    meta_dst = MetaData()
    meta_src.reflect(bind=src_engine)
    meta_dst.reflect(bind=dst_engine)

    tables_order = [
        "tipos_despesa",
        "produtos",
        "clientes",
        "caixa_sessoes",
        "vendas",
        "itens_venda",
        "fiados",
        "fluxo_caixa",
    ]

    with src_engine.connect() as src_conn, dst_engine.begin() as dst_conn:
        dst_conn.execute(text("set session_replication_role = replica"))
        for tname in tables_order:
            if tname not in meta_src.tables or tname not in meta_dst.tables:
                continue
            t_src = meta_src.tables[tname]
            t_dst = meta_dst.tables[tname]

            rows = fetch_all(src_conn, t_src)
            if not rows:
                continue

            dst_conn.execute(text(f"delete from {tname}"))
            bulk_insert(dst_conn, t_dst, rows)
            set_sequence(dst_conn, tname)
            print(f"Migrado: {tname} ({len(rows)})")
        dst_conn.execute(text("set session_replication_role = origin"))

    print("OK: migração concluída.")


if __name__ == "__main__":
    main()

