import os
import logging
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from app.core.models import Base
from app.core.resources import app_data_path
from app.core.config import load_settings

# Configuração de logs
os.makedirs(app_data_path("logs"), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=app_data_path("logs", "database.log"),
    filemode='a'
)
logger = logging.getLogger('Database')

engine = None
SessionLocal = sessionmaker(autocommit=False, autoflush=False)
db_session = scoped_session(SessionLocal)


def get_database_url() -> str:
    """Resolve a URL do banco (env DATABASE_URL > settings.database_url > SQLite local)."""
    env_url = (os.getenv("DATABASE_URL") or "").strip()
    if env_url:
        return env_url

    try:
        s = load_settings()
        cfg_url = (s.get("database_url") or "").strip()
        if cfg_url:
            return cfg_url
    except Exception:
        pass

    db_path = app_data_path("database.db")
    return f"sqlite:///{db_path}"


def redact_database_url(url: str) -> str:
    """Oculta a senha de uma URL de conexão para exibição segura."""
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


def get_database_status() -> dict:
    """Retorna status da conexão atual (dialeto, URL mascarada e conectividade)."""
    url = get_database_url()
    try:
        eng = init_engine()
        with eng.connect() as conn:
            conn.execute(text("select 1"))
        return {
            "connected": True,
            "dialect": eng.dialect.name,
            "url": redact_database_url(url),
            "message": "Conexão ativa",
        }
    except Exception as e:
        return {
            "connected": False,
            "dialect": "desconhecido",
            "url": redact_database_url(url),
            "message": str(e),
        }


def init_engine():
    """Inicializa o engine e configura a SessionLocal (lazy init)."""
    global engine
    if engine is not None:
        return engine

    url = get_database_url()
    connect_args = {}
    if url.startswith("sqlite:///"):
        connect_args = {"check_same_thread": False}

    engine = create_engine(url, echo=False, pool_pre_ping=True, connect_args=connect_args)
    SessionLocal.configure(bind=engine)
    return engine

def _sqlite_column_exists(table_name: str, column_name: str) -> bool:
    """Verifica existência de coluna via PRAGMA table_info (SQLite)."""
    try:
        init_engine()
        with engine.connect() as conn:
            rows = conn.exec_driver_sql(f"PRAGMA table_info({table_name})").fetchall()
        return any(r[1] == column_name for r in rows)
    except Exception:
        return False


def _sqlite_add_column(table_name: str, ddl: str):
    """Adiciona coluna com ALTER TABLE no SQLite (DDL simples)."""
    init_engine()
    with engine.connect() as conn:
        conn.exec_driver_sql(f"ALTER TABLE {table_name} ADD COLUMN {ddl}")


def _apply_light_migrations():
    """Aplica migrações leves para compatibilidade com SQLite sem Alembic."""
    try:
        init_engine()
        if engine.dialect.name != "sqlite":
            return

        if not _sqlite_column_exists("fluxo_caixa", "caixa_sessao_id"):
            _sqlite_add_column("fluxo_caixa", "caixa_sessao_id INTEGER")
            logger.info("Migração aplicada: fluxo_caixa.caixa_sessao_id")

        if not _sqlite_column_exists("vendas", "caixa_sessao_id"):
            _sqlite_add_column("vendas", "caixa_sessao_id INTEGER")
            logger.info("Migração aplicada: vendas.caixa_sessao_id")

        if not _sqlite_column_exists("fluxo_caixa", "meio_pagamento"):
            _sqlite_add_column("fluxo_caixa", "meio_pagamento VARCHAR(20)")
            logger.info("Migração aplicada: fluxo_caixa.meio_pagamento")
    except Exception as e:
        logger.error(f"Erro em migração leve: {e}")


def init_db():
    """Inicializa o banco de dados e cria todas as tabelas se não existirem."""
    try:
        init_engine()
        # Garante que os diretórios necessários existam
        required_dirs = ['relatorios', 'config', 'logs']
        for d in required_dirs:
            full = app_data_path(d)
            if not os.path.exists(full):
                os.makedirs(full, exist_ok=True)
                logger.info(f"Diretório criado: {full}")

        # Cria as tabelas no banco de dados
        Base.metadata.create_all(bind=engine)
        _apply_light_migrations()
        
        # Inserir categorias de despesas padrão se a tabela estiver vazia
        from app.core.models import TipoDespesa
        if db_session.query(TipoDespesa).count() == 0:
            categorias_padrao = [
                "Fornecedor de Bebidas", "Fornecedor de Alimentos", 
                "Aluguel / Condomínio", "Energia / Água / Internet",
                "Funcionários / Diárias", "Impostos / Taxas", 
                "Retirada Sócio", "Outras Despesas"
            ]
            for nome in categorias_padrao:
                db_session.add(TipoDespesa(nome=nome, ativo=1))
            db_session.commit()
            logger.info("Categorias de despesas padrão inseridas.")

        logger.info("Banco de dados e tabelas inicializados com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao inicializar o banco de dados: {e}")
        raise

def get_db():
    """Retorna uma nova sessão de banco de dados."""
    return db_session()


def refresh_db_session(hard: bool = False):
    """Atualiza o estado da sessão para evitar leitura de dados cacheados em multiusuário.

    hard=False: expira entidades e força recarga na próxima consulta, sem derrubar a sessão.
    hard=True : faz rollback (se possível) e recria a sessão por completo.
    """
    try:
        sess = db_session()
        sess.expire_all()
    except Exception:
        pass

    if not hard:
        return

    try:
        db_session.rollback()
    except Exception:
        pass
    try:
        db_session.remove()
    except Exception:
        pass

if __name__ == "__main__":
    init_db()
    print(f"Banco de dados inicializado em: {get_database_url()}")
