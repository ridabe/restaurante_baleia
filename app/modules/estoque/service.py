import logging
from app.core.database import db_session
from app.core.models import Produto

logger = logging.getLogger('EstoqueService')

class EstoqueService:
    """Serviço para gerenciar operações de estoque no banco de dados."""

    @staticmethod
    def get_todos():
        """Retorna todos os produtos do estoque."""
        try:
            return db_session.query(Produto).all()
        except Exception as e:
            logger.error(f"Erro ao buscar produtos: {e}")
            return []

    @staticmethod
    def buscar_por_id(id_produto):
        """Busca um produto específico pelo ID."""
        try:
            return db_session.query(Produto).filter(Produto.id == id_produto).first()
        except Exception as e:
            logger.error(f"Erro ao buscar produto por ID: {e}")
            return None

    @staticmethod
    def adicionar(codigo, nome, preco, quantidade, estoque_minimo=5):
        """Adiciona um novo produto ao estoque."""
        try:
            novo_produto = Produto(
                codigo=codigo,
                nome=nome,
                preco=preco,
                quantidade=quantidade,
                estoque_minimo=estoque_minimo
            )
            db_session.add(novo_produto)
            db_session.commit()
            logger.info(f"Produto adicionado: {nome} (Cód: {codigo})")
            return True, "Produto adicionado com sucesso."
        except Exception as e:
            db_session.rollback()
            logger.error(f"Erro ao adicionar produto: {e}")
            return False, f"Erro ao adicionar: Já existe um produto com este código ou erro no banco."

    @staticmethod
    def atualizar(id_produto, codigo=None, nome=None, preco=None, quantidade=None, estoque_minimo=None):
        """Atualiza informações de um produto existente."""
        try:
            produto = EstoqueService.buscar_por_id(id_produto)
            if not produto:
                return False, "Produto não encontrado."

            if codigo is not None: produto.codigo = codigo
            if nome is not None: produto.nome = nome
            if preco is not None: produto.preco = preco
            if quantidade is not None: produto.quantidade = quantidade
            if estoque_minimo is not None: produto.estoque_minimo = estoque_minimo

            db_session.commit()
            logger.info(f"Produto atualizado: {produto.nome}")
            return True, "Produto atualizado com sucesso."
        except Exception as e:
            db_session.rollback()
            logger.error(f"Erro ao atualizar produto: {e}")
            return False, f"Erro ao atualizar: {e}"

    @staticmethod
    def deletar(id_produto):
        """Remove um produto do estoque."""
        try:
            produto = EstoqueService.buscar_por_id(id_produto)
            if not produto:
                return False, "Produto não encontrado."

            db_session.delete(produto)
            db_session.commit()
            logger.info(f"Produto deletado: {id_produto}")
            return True, "Produto removido com sucesso."
        except Exception as e:
            db_session.rollback()
            logger.error(f"Erro ao deletar produto: {e}")
            return False, f"Erro ao deletar: {e}"

    @staticmethod
    def alerta_estoque_baixo():
        """Retorna lista de produtos com quantidade abaixo do mínimo."""
        try:
            return db_session.query(Produto).filter(Produto.quantidade <= Produto.estoque_minimo).all()
        except Exception as e:
            logger.error(f"Erro ao buscar alertas de estoque: {e}")
            return []
