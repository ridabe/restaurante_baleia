import logging
from datetime import datetime

from sqlalchemy import func

from app.core.database import db_session
from app.core.models import CaixaSessao, FluxoCaixa

logger = logging.getLogger("CaixaSessaoService")


class CaixaSessaoService:
    """Serviço de sessão de caixa (abertura/fechamento) para controle operacional."""

    @staticmethod
    def get_sessao_aberta():
        """Retorna a sessão de caixa aberta (se existir)."""
        try:
            return (
                db_session.query(CaixaSessao)
                .filter(CaixaSessao.status == "ABERTO")
                .order_by(CaixaSessao.aberta_em.desc())
                .first()
            )
        except Exception as e:
            logger.error(f"Erro ao buscar sessão aberta: {e}")
            return None

    @staticmethod
    def abrir_caixa(valor_abertura: float, observacao: str = ""):
        """Abre uma sessão de caixa. Se já existir sessão aberta, bloqueia."""
        try:
            aberta = CaixaSessaoService.get_sessao_aberta()
            if aberta:
                return False, "Já existe um caixa aberto."

            sessao = CaixaSessao(
                aberta_em=datetime.now(),
                valor_abertura=float(valor_abertura),
                status="ABERTO",
                observacao=(observacao or "")[:200] or None,
            )
            db_session.add(sessao)
            db_session.flush()

            mov = FluxoCaixa(
                tipo="ABERTURA_CAIXA",
                meio_pagamento="DINHEIRO",
                valor=float(valor_abertura),
                descricao=f"Abertura de caixa (Sessão #{sessao.id})",
                caixa_sessao_id=sessao.id,
            )
            db_session.add(mov)
            db_session.commit()
            return True, f"Caixa aberto com sucesso (Sessão #{sessao.id})."
        except Exception as e:
            db_session.rollback()
            logger.error(f"Erro ao abrir caixa: {e}")
            return False, str(e)

    @staticmethod
    def calcular_totais_sessao(sessao_id: int) -> dict:
        """Calcula totais da sessão (geral e dinheiro) e saldo esperado da gaveta."""
        sessao = db_session.query(CaixaSessao).filter(CaixaSessao.id == sessao_id).first()
        if not sessao:
            return {
                "entradas": 0.0,
                "saidas": 0.0,
                "entradas_dinheiro": 0.0,
                "saidas_dinheiro": 0.0,
                "saldo_esperado": 0.0,
            }

        entradas = (
            db_session.query(func.sum(FluxoCaixa.valor))
            .filter(
                FluxoCaixa.caixa_sessao_id == sessao_id,
                FluxoCaixa.tipo == "ENTRADA",
            )
            .scalar()
            or 0.0
        )
        saidas = (
            db_session.query(func.sum(FluxoCaixa.valor))
            .filter(
                FluxoCaixa.caixa_sessao_id == sessao_id,
                FluxoCaixa.tipo == "SAIDA",
            )
            .scalar()
            or 0.0
        )

        entradas_dinheiro = (
            db_session.query(func.sum(FluxoCaixa.valor))
            .filter(
                FluxoCaixa.caixa_sessao_id == sessao_id,
                FluxoCaixa.tipo == "ENTRADA",
                FluxoCaixa.meio_pagamento == "DINHEIRO",
            )
            .scalar()
            or 0.0
        )
        saidas_dinheiro = (
            db_session.query(func.sum(FluxoCaixa.valor))
            .filter(
                FluxoCaixa.caixa_sessao_id == sessao_id,
                FluxoCaixa.tipo == "SAIDA",
                FluxoCaixa.meio_pagamento == "DINHEIRO",
            )
            .scalar()
            or 0.0
        )

        saldo_esperado = (
            float(sessao.valor_abertura or 0.0)
            + float(entradas_dinheiro)
            - float(saidas_dinheiro)
        )
        return {
            "entradas": float(entradas),
            "saidas": float(saidas),
            "entradas_dinheiro": float(entradas_dinheiro),
            "saidas_dinheiro": float(saidas_dinheiro),
            "saldo_esperado": float(saldo_esperado),
        }

    @staticmethod
    def fechar_caixa(valor_contado: float, observacao: str = ""):
        """Fecha a sessão aberta calculando saldo esperado e diferença."""
        try:
            sessao = CaixaSessaoService.get_sessao_aberta()
            if not sessao:
                return False, "Não existe caixa aberto para fechar."

            totals = CaixaSessaoService.calcular_totais_sessao(sessao.id)
            saldo_esperado = float(totals["saldo_esperado"])
            contado = float(valor_contado)
            diferenca = contado - saldo_esperado

            sessao.fechada_em = datetime.now()
            sessao.valor_contado = contado
            sessao.saldo_esperado = saldo_esperado
            sessao.diferenca = diferenca
            sessao.status = "FECHADO"
            sessao.observacao = (observacao or sessao.observacao or "")[:200] or None

            desc = (
                f"Fechamento de caixa (Sessão #{sessao.id}) | "
                f"Esperado: R$ {saldo_esperado:.2f} | Contado: R$ {contado:.2f} | Diferença: R$ {diferenca:.2f}"
            )
            mov = FluxoCaixa(
                tipo="FECHAMENTO_CAIXA",
                meio_pagamento="DINHEIRO",
                valor=0.0,
                descricao=desc[:200],
                caixa_sessao_id=sessao.id,
            )
            db_session.add(mov)
            db_session.commit()
            return True, f"Caixa fechado com sucesso (Sessão #{sessao.id})."
        except Exception as e:
            db_session.rollback()
            logger.error(f"Erro ao fechar caixa: {e}")
            return False, str(e)
