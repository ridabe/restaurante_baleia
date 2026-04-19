import logging
from app.core.database import db_session
from app.core.models import Cliente, Fiado, FluxoCaixa

logger = logging.getLogger('FiadoService')

class FiadoService:
    """Serviço para gerenciar clientes e suas dívidas."""

    @staticmethod
    def get_todos_clientes():
        """Retorna todos os clientes."""
        try:
            return db_session.query(Cliente).all()
        except Exception as e:
            logger.error(f"Erro ao buscar clientes: {e}")
            return []

    @staticmethod
    def buscar_cliente_por_id(id_cliente):
        """Busca um cliente específico pelo ID."""
        try:
            return db_session.query(Cliente).filter(Cliente.id == id_cliente).first()
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por ID: {e}")
            return None

    @staticmethod
    def cadastrar_cliente(nome, telefone=None, email=None):
        """Cadastra um novo cliente."""
        try:
            novo_cliente = Cliente(nome=nome, telefone=telefone, email=email)
            db_session.add(novo_cliente)
            db_session.commit()
            logger.info(f"Cliente cadastrado: {nome}")
            return True, "Cliente cadastrado com sucesso."
        except Exception as e:
            db_session.rollback()
            logger.error(f"Erro ao cadastrar cliente: {e}")
            return False, f"Erro ao cadastrar: {e}"

    @staticmethod
    def registrar_fiado(id_cliente, valor, descricao):
        """Registra uma compra fiada para um cliente."""
        try:
            cliente = FiadoService.buscar_cliente_por_id(id_cliente)
            if not cliente:
                return False, "Cliente não encontrado."

            # Cria registro de fiado (Débito)
            novo_fiado = Fiado(
                cliente_id=id_cliente,
                valor=valor,
                tipo='DEBITO',
                descricao=descricao
            )
            
            # Atualiza a dívida do cliente
            cliente.divida_atual += valor
            
            db_session.add(novo_fiado)
            db_session.commit()
            logger.info(f"Dívida de R$ {valor:.2f} registrada para: {cliente.nome}")
            return True, "Compra fiada registrada com sucesso."
        except Exception as e:
            db_session.rollback()
            logger.error(f"Erro ao registrar fiado: {e}")
            return False, f"Erro ao registrar: {e}"

    @staticmethod
    def pagar_divida(id_cliente, valor, descricao="Pagamento de dívida"):
        """Registra um pagamento de dívida de um cliente."""
        try:
            cliente = FiadoService.buscar_cliente_por_id(id_cliente)
            if not cliente:
                return False, "Cliente não encontrado."

            if valor <= 0:
                return False, "O valor do pagamento deve ser maior que zero."

            # Cria registro de fiado (Crédito)
            novo_pagamento = Fiado(
                cliente_id=id_cliente,
                valor=valor,
                tipo='CREDITO',
                descricao=descricao
            )
            
            # Atualiza a dívida do cliente
            divida_antes = float(cliente.divida_atual or 0.0)
            cliente.divida_atual = max(0.0, divida_antes - float(valor))
            
            # Registra no Fluxo de Caixa como entrada
            saldo_restante = float(cliente.divida_atual or 0.0)
            descricao_fluxo = (
                f"Pagamento de dívida | Cliente: {cliente.nome} | "
                f"Pago: R$ {float(valor):.2f} | Saldo restante: R$ {saldo_restante:.2f}"
            )
            if descricao:
                descricao_fluxo += f" | Obs: {descricao}"

            try:
                from app.modules.caixa_sessao.service import CaixaSessaoService
                sessao = CaixaSessaoService.get_sessao_aberta()
                sessao_id = sessao.id if sessao else None
            except Exception:
                sessao_id = None

            novo_fluxo = FluxoCaixa(
                tipo='ENTRADA',
                valor=valor,
                descricao=descricao_fluxo[:200],
                caixa_sessao_id=sessao_id
            )
            
            db_session.add(novo_pagamento)
            db_session.add(novo_fluxo)

            db_session.commit()
            logger.info(f"Pagamento de R$ {valor:.2f} recebido de: {cliente.nome}")
            return True, "Pagamento registrado com sucesso."
        except Exception as e:
            db_session.rollback()
            logger.error(f"Erro ao registrar pagamento: {e}")
            return False, f"Erro ao registrar: {e}"

    @staticmethod
    def deletar_cliente(id_cliente):
        """Remove um cliente e seus registros de fiado."""
        try:
            cliente = FiadoService.buscar_cliente_por_id(id_cliente)
            if not cliente:
                return False, "Cliente não encontrado."

            # Deleta os fiados associados
            db_session.query(Fiado).filter(Fiado.cliente_id == id_cliente).delete()
            
            db_session.delete(cliente)
            db_session.commit()
            logger.info(f"Cliente e registros deletados: {id_cliente}")
            return True, "Cliente removido com sucesso."
        except Exception as e:
            db_session.rollback()
            logger.error(f"Erro ao deletar cliente: {e}")
            return False, f"Erro ao deletar: {e}"
