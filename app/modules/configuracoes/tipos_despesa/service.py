import logging
from sqlalchemy import func
from app.core.database import db_session
from app.core.models import TipoDespesa, FluxoCaixa

logger = logging.getLogger('TipoDespesaService')

class TipoDespesaService:
    """Serviço para gerenciar tipos de despesas."""

    @staticmethod
    def get_todos():
        """Retorna todos os tipos de despesas cadastrados."""
        try:
            return db_session.query(TipoDespesa).all()
        except Exception as e:
            logger.error(f"Erro ao buscar tipos de despesas: {e}")
            return []

    @staticmethod
    def get_ativos():
        """Retorna apenas os tipos de despesas ativos."""
        try:
            return db_session.query(TipoDespesa).filter(TipoDespesa.ativo == 1).all()
        except Exception as e:
            logger.error(f"Erro ao buscar tipos de despesas ativos: {e}")
            return []

    @staticmethod
    def buscar_por_id(id_tipo):
        """Busca um tipo de despesa pelo ID."""
        try:
            return db_session.query(TipoDespesa).filter(TipoDespesa.id == id_tipo).first()
        except Exception as e:
            logger.error(f"Erro ao buscar tipo de despesa por ID {id_tipo}: {e}")
            return None

    @staticmethod
    def cadastrar(nome, descricao=""):
        """Cadastra um novo tipo de despesa."""
        nome = nome.strip()
        if not nome:
            return False, "O nome do tipo de despesa é obrigatório."

        try:
            # Validar duplicidade (case-insensitive)
            existente = db_session.query(TipoDespesa).filter(
                func.lower(TipoDespesa.nome) == nome.lower()
            ).first()
            
            if existente:
                return False, f"O tipo de despesa '{nome}' já está cadastrado."

            novo_tipo = TipoDespesa(
                nome=nome,
                descricao=descricao,
                ativo=1
            )
            db_session.add(novo_tipo)
            db_session.commit()
            return True, "Tipo de despesa cadastrado com sucesso."
        except Exception as e:
            db_session.rollback()
            logger.error(f"Erro ao cadastrar tipo de despesa: {e}")
            return False, str(e)

    @staticmethod
    def atualizar(id_tipo, nome, descricao, ativo):
        """Atualiza um tipo de despesa existente."""
        nome = nome.strip()
        if not nome:
            return False, "O nome do tipo de despesa é obrigatório."

        try:
            tipo = db_session.query(TipoDespesa).filter(TipoDespesa.id == id_tipo).first()
            if not tipo:
                return False, "Tipo de despesa não encontrado."

            # Validar duplicidade se o nome mudou
            if nome.lower() != tipo.nome.lower():
                existente = db_session.query(TipoDespesa).filter(
                    func.lower(TipoDespesa.nome) == nome.lower()
                ).first()
                if existente:
                    return False, f"Já existe outro tipo de despesa com o nome '{nome}'."

            tipo.nome = nome
            tipo.descricao = descricao
            tipo.ativo = 1 if ativo else 0
            
            db_session.commit()
            return True, "Tipo de despesa atualizado com sucesso."
        except Exception as e:
            db_session.rollback()
            logger.error(f"Erro ao atualizar tipo de despesa: {e}")
            return False, str(e)

    @staticmethod
    def deletar(id_tipo):
        """Remove um tipo de despesa ou inativa se houver vínculos."""
        try:
            tipo = db_session.query(TipoDespesa).filter(TipoDespesa.id == id_tipo).first()
            if not tipo:
                return False, "Tipo de despesa não encontrado."

            # Verificar se existem movimentações vinculadas
            vinculos = db_session.query(FluxoCaixa).filter(FluxoCaixa.tipo_despesa_id == id_tipo).count()
            
            if vinculos > 0:
                # Se houver vínculos, apenas inativa
                tipo.ativo = 0
                db_session.commit()
                return True, f"O tipo '{tipo.nome}' não pôde ser excluído pois possui {vinculos} movimentações vinculadas. Ele foi inativado para preservar o histórico."
            
            # Se não houver vínculos, exclui fisicamente
            db_session.delete(tipo)
            db_session.commit()
            return True, "Tipo de despesa excluído com sucesso."
        except Exception as e:
            db_session.rollback()
            logger.error(f"Erro ao excluir tipo de despesa: {e}")
            return False, str(e)
