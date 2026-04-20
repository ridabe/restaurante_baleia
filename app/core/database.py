import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.core.models import Base
from app.core.resources import app_data_path

# Configuração de logs
os.makedirs(app_data_path("logs"), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=app_data_path("logs", "database.log"),
    filemode='a'
)
logger = logging.getLogger('Database')

# Caminho para o banco de dados
DB_NAME = "database.db"
DB_PATH = app_data_path(DB_NAME)
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Criação do motor e da sessão
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

def _sqlite_column_exists(table_name: str, column_name: str) -> bool:
    """Verifica existência de coluna via PRAGMA table_info (SQLite)."""
    try:
        with engine.connect() as conn:
            rows = conn.exec_driver_sql(f"PRAGMA table_info({table_name})").fetchall()
        return any(r[1] == column_name for r in rows)
    except Exception:
        return False


def _sqlite_add_column(table_name: str, ddl: str):
    """Adiciona coluna com ALTER TABLE no SQLite (DDL simples)."""
    with engine.connect() as conn:
        conn.exec_driver_sql(f"ALTER TABLE {table_name} ADD COLUMN {ddl}")


def _apply_light_migrations():
    """Aplica migrações leves para compatibilidade com SQLite sem Alembic."""
    try:
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

if __name__ == "__main__":
    init_db()
    print(f"Banco de dados inicializado em: {DB_PATH}")
