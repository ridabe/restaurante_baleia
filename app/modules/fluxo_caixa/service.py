import logging
from datetime import datetime, date, timedelta
from sqlalchemy import func
from app.core.database import db_session
from app.core.models import FluxoCaixa

logger = logging.getLogger('FluxoCaixaService')

class FluxoCaixaService:
    """Serviço para gerenciar entradas, saídas e relatórios financeiros."""

    @staticmethod
    def get_saldo_atual():
        """Calcula o saldo atual baseado em todas as entradas e saídas."""
        try:
            # Entradas: ENTRADA, ABERTURA_CAIXA
            entradas = db_session.query(func.sum(FluxoCaixa.valor)).filter(
                FluxoCaixa.tipo.in_(['ENTRADA', 'ABERTURA_CAIXA'])
            ).scalar() or 0.0
            
            # Saídas: SAIDA, FECHAMENTO_CAIXA (se houver retirada)
            saidas = db_session.query(func.sum(FluxoCaixa.valor)).filter(
                FluxoCaixa.tipo.in_(['SAIDA', 'FECHAMENTO_CAIXA'])
            ).scalar() or 0.0
            
            return entradas - saidas
        except Exception as e:
            logger.error(f"Erro ao calcular saldo atual: {e}")
            return 0.0

    @staticmethod
    def registrar_saida(valor, descricao, tipo_despesa_id=None):
        """Registra uma saída de caixa (despesa)."""
        try:
            nova_saida = FluxoCaixa(
                tipo='SAIDA',
                valor=valor,
                descricao=descricao,
                tipo_despesa_id=tipo_despesa_id
            )
            db_session.add(nova_saida)
            db_session.commit()
            logger.info(f"Saída de R$ {valor:.2f} registrada: {descricao} (ID Categoria: {tipo_despesa_id})")
            return True, "Saída registrada com sucesso."
        except Exception as e:
            db_session.rollback()
            logger.error(f"Erro ao registrar saída: {e}")
            return False, str(e)

    @staticmethod
    def get_relatorio_diario(data=None):
        """Retorna todas as movimentações de um dia específico."""
        if data is None:
            data = date.today()
        
        proximo_dia = data + timedelta(days=1)
        
        try:
            return db_session.query(FluxoCaixa).filter(
                FluxoCaixa.data_registro >= data,
                FluxoCaixa.data_registro < proximo_dia
            ).all()
        except Exception as e:
            logger.error(f"Erro ao buscar relatório diário: {e}")
            return []

    @staticmethod
    def get_movimentacoes_por_periodo(data_inicio, data_fim, incluir_venda_fiado: bool = False):
        """Retorna movimentações em um intervalo de datas (por padrão, oculta VENDA_FIADO)."""
        try:
            # Garante que data_fim inclua todo o dia (até 23:59:59)
            if isinstance(data_fim, date) and not isinstance(data_fim, datetime):
                data_fim_dt = datetime.combine(data_fim, datetime.max.time())
            else:
                data_fim_dt = data_fim

            if isinstance(data_inicio, date) and not isinstance(data_inicio, datetime):
                data_inicio_dt = datetime.combine(data_inicio, datetime.min.time())
            else:
                data_inicio_dt = data_inicio

            query = db_session.query(FluxoCaixa).filter(
                FluxoCaixa.data_registro >= data_inicio_dt,
                FluxoCaixa.data_registro <= data_fim_dt
            )
            if not incluir_venda_fiado:
                query = query.filter(FluxoCaixa.tipo != "VENDA_FIADO")
            return query.order_by(FluxoCaixa.data_registro.desc()).all()
        except Exception as e:
            logger.error(f"Erro ao buscar movimentações por período: {e}")
            return []

    @staticmethod
    def get_resumo_mes(mes=None, ano=None):
        """Retorna totais de entrada e saída de um mês."""
        hoje = date.today()
        mes = mes or hoje.month
        ano = ano or hoje.year
        
        try:
            # Simplificando a busca por mês/ano usando string_format se necessário, 
            # ou filtros de data. Para SQLite, filtros de data funcionam bem.
            data_inicio = date(ano, mes, 1)
            if mes == 12:
                data_fim = date(ano + 1, 1, 1)
            else:
                data_fim = date(ano, mes + 1, 1)

            entradas = db_session.query(func.sum(FluxoCaixa.valor)).filter(
                FluxoCaixa.tipo.in_(['ENTRADA', 'ABERTURA_CAIXA']),
                FluxoCaixa.data_registro >= data_inicio,
                FluxoCaixa.data_registro < data_fim
            ).scalar() or 0.0
            
            saidas = db_session.query(func.sum(FluxoCaixa.valor)).filter(
                FluxoCaixa.tipo.in_(['SAIDA', 'FECHAMENTO_CAIXA']),
                FluxoCaixa.data_registro >= data_inicio,
                FluxoCaixa.data_registro < data_fim
            ).scalar() or 0.0
            
            return {
                "entradas": entradas,
                "saidas": saidas,
                "saldo": entradas - saidas
            }
        except Exception as e:
            logger.error(f"Erro ao buscar resumo mensal: {e}")
            return {"entradas": 0.0, "saidas": 0.0, "saldo": 0.0}
