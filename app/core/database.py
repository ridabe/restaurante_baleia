import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.core.models import Base

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/database.log',
    filemode='a'
)
logger = logging.getLogger('Database')

# Caminho para o banco de dados
DB_NAME = "database.db"
DB_PATH = os.path.join(os.getcwd(), DB_NAME)
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Criação do motor e da sessão
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

def init_db():
    """Inicializa o banco de dados e cria todas as tabelas se não existirem."""
    try:
        # Garante que os diretórios necessários existam
        required_dirs = ['relatorios', 'config', 'logs']
        for d in required_dirs:
            if not os.path.exists(d):
                os.makedirs(d)
                logger.info(f"Diretório criado: {d}")

        # Cria as tabelas no banco de dados
        Base.metadata.create_all(bind=engine)
        
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
