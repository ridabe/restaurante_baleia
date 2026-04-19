from __future__ import annotations

import logging
from datetime import date, datetime, time, timedelta

from sqlalchemy import func

from app.core.config import load_settings
from app.core.database import db_session
from app.core.models import CaixaSessao, Cliente, FluxoCaixa, ItemVenda, Produto, TipoDespesa, Venda

logger = logging.getLogger("DashboardService")


class DashboardService:
    """Serviço de agregação para o dashboard gerencial e operacional."""

    def get_snapshot(self, period_days: int = 7) -> dict:
        """Consolida todos os blocos de dados do dashboard em uma única estrutura."""
        safe_days = 1 if period_days <= 1 else (30 if period_days >= 30 else 7)
        try:
            return {
                "cards": self._build_cards_with_trends(),
                "series_financeira": self._build_entradas_saidas_series(safe_days),
                "despesas_categoria": self._build_despesas_por_categoria(safe_days),
                "top_produtos": self._build_top_produtos(safe_days),
                "estoque_baixo": self._build_estoque_baixo(),
                "fiado": self._build_fiado_data(),
                "movimentacoes_recentes": self._build_recent_movements(limit=10),
                "updated_at": datetime.now(),
            }
        except Exception as e:
            logger.error(f"Erro ao montar snapshot do dashboard: {e}")
            return {
                "cards": {},
                "series_financeira": {"labels": [], "entradas": [], "saidas": []},
                "despesas_categoria": [],
                "top_produtos": [],
                "estoque_baixo": [],
                "fiado": {"total": 0.0, "qtd_clientes": 0, "top_clientes": []},
                "movimentacoes_recentes": [],
                "updated_at": datetime.now(),
            }

    def _build_cards_with_trends(self) -> dict:
        """Calcula KPIs do dia e inclui tendências vs ontem (entradas/saídas/saldo)."""
        inicio_dia = datetime.combine(date.today(), time.min)
        fim_dia = datetime.combine(date.today(), time.max)
        inicio_ontem = datetime.combine(date.today() - timedelta(days=1), time.min)
        fim_ontem = datetime.combine(date.today() - timedelta(days=1), time.max)

        entradas_dia = (
            db_session.query(func.sum(FluxoCaixa.valor))
            .filter(
                FluxoCaixa.tipo == "ENTRADA",
                FluxoCaixa.data_registro >= inicio_dia,
                FluxoCaixa.data_registro <= fim_dia,
            )
            .scalar()
            or 0.0
        )
        saidas_dia = (
            db_session.query(func.sum(FluxoCaixa.valor))
            .filter(
                FluxoCaixa.tipo == "SAIDA",
                FluxoCaixa.data_registro >= inicio_dia,
                FluxoCaixa.data_registro <= fim_dia,
            )
            .scalar()
            or 0.0
        )
        saldo_dia = float(entradas_dia) - float(saidas_dia)

        entradas_ontem = (
            db_session.query(func.sum(FluxoCaixa.valor))
            .filter(
                FluxoCaixa.tipo == "ENTRADA",
                FluxoCaixa.data_registro >= inicio_ontem,
                FluxoCaixa.data_registro <= fim_ontem,
            )
            .scalar()
            or 0.0
        )
        saidas_ontem = (
            db_session.query(func.sum(FluxoCaixa.valor))
            .filter(
                FluxoCaixa.tipo == "SAIDA",
                FluxoCaixa.data_registro >= inicio_ontem,
                FluxoCaixa.data_registro <= fim_ontem,
            )
            .scalar()
            or 0.0
        )
        saldo_ontem = float(entradas_ontem) - float(saidas_ontem)

        total_fiado = (
            db_session.query(func.sum(Cliente.divida_atual))
            .filter(Cliente.divida_atual > 0)
            .scalar()
            or 0.0
        )
        qtd_clientes_fiado = (
            db_session.query(func.count(Cliente.id))
            .filter(Cliente.divida_atual > 0)
            .scalar()
            or 0
        )

        status_caixa = self._get_status_caixa()

        return {
            "entradas_dia": float(entradas_dia),
            "saidas_dia": float(saidas_dia),
            "saldo_dia": float(saldo_dia),
            "entradas_ontem": float(entradas_ontem),
            "saidas_ontem": float(saidas_ontem),
            "saldo_ontem": float(saldo_ontem),
            "total_fiado": float(total_fiado),
            "qtd_clientes_fiado": int(qtd_clientes_fiado),
            "status_caixa": status_caixa,
        }

    def _get_status_caixa(self) -> dict:
        """Determina status do caixa com base na sessão de caixa (CaixaSessao)."""
        aberta = (
            db_session.query(CaixaSessao)
            .filter(CaixaSessao.status == "ABERTO")
            .order_by(CaixaSessao.aberta_em.desc())
            .first()
        )
        if aberta:
            return {
                "label": "Caixa Aberto",
                "detalhe": f"Aberto às {aberta.aberta_em.strftime('%H:%M')}",
            }

        ultima = db_session.query(CaixaSessao).order_by(CaixaSessao.aberta_em.desc()).first()
        if not ultima:
            return {"label": "Não iniciado", "detalhe": "Sem abertura registrada"}

        if ultima.fechada_em:
            return {"label": "Caixa Fechado", "detalhe": f"Fechado às {ultima.fechada_em.strftime('%H:%M')}"}
        return {"label": "Caixa Fechado", "detalhe": "Sem fechamento registrado"}

    def _build_entradas_saidas_series(self, period_days: int) -> dict:
        """Monta série diária (últimos N dias) para gráfico de entradas x saídas."""
        start_date = date.today() - timedelta(days=period_days - 1)
        start_dt = datetime.combine(start_date, time.min)
        end_dt = datetime.combine(date.today(), time.max)

        entradas_rows = (
            db_session.query(
                func.date(FluxoCaixa.data_registro).label("dia"),
                func.sum(FluxoCaixa.valor).label("valor"),
            )
            .filter(
                FluxoCaixa.tipo == "ENTRADA",
                FluxoCaixa.data_registro >= start_dt,
                FluxoCaixa.data_registro <= end_dt,
            )
            .group_by(func.date(FluxoCaixa.data_registro))
            .all()
        )
        saidas_rows = (
            db_session.query(
                func.date(FluxoCaixa.data_registro).label("dia"),
                func.sum(FluxoCaixa.valor).label("valor"),
            )
            .filter(
                FluxoCaixa.tipo == "SAIDA",
                FluxoCaixa.data_registro >= start_dt,
                FluxoCaixa.data_registro <= end_dt,
            )
            .group_by(func.date(FluxoCaixa.data_registro))
            .all()
        )

        entradas_map = {str(r.dia): float(r.valor or 0.0) for r in entradas_rows}
        saidas_map = {str(r.dia): float(r.valor or 0.0) for r in saidas_rows}

        labels = []
        entradas = []
        saidas = []
        for i in range(period_days):
            d = start_date + timedelta(days=i)
            key = d.isoformat()
            labels.append(d.strftime("%d/%m"))
            entradas.append(entradas_map.get(key, 0.0))
            saidas.append(saidas_map.get(key, 0.0))

        return {"labels": labels, "entradas": entradas, "saidas": saidas}

    def _build_despesas_por_categoria(self, period_days: int) -> list[dict]:
        """Agrupa despesas por categoria no período selecionado para análise gerencial."""
        start_date = date.today() - timedelta(days=period_days - 1)
        start_dt = datetime.combine(start_date, time.min)
        end_dt = datetime.combine(date.today(), time.max)

        rows = (
            db_session.query(
                TipoDespesa.nome.label("categoria"),
                func.sum(FluxoCaixa.valor).label("total"),
            )
            .join(TipoDespesa, TipoDespesa.id == FluxoCaixa.tipo_despesa_id, isouter=True)
            .filter(
                FluxoCaixa.tipo == "SAIDA",
                FluxoCaixa.data_registro >= start_dt,
                FluxoCaixa.data_registro <= end_dt,
            )
            .group_by(TipoDespesa.nome)
            .order_by(func.sum(FluxoCaixa.valor).desc())
            .all()
        )
        data = []
        for row in rows:
            data.append(
                {
                    "categoria": row.categoria or "Sem categoria",
                    "valor": float(row.total or 0.0),
                }
            )
        return data

    def _build_top_produtos(self, period_days: int, limit: int = 10) -> list[dict]:
        """Retorna ranking de produtos mais vendidos por quantidade e valor no período."""
        start_date = date.today() - timedelta(days=period_days - 1)
        start_dt = datetime.combine(start_date, time.min)
        end_dt = datetime.combine(date.today(), time.max)

        rows = (
            db_session.query(
                Produto.nome.label("produto"),
                func.sum(ItemVenda.quantidade).label("qtd"),
                func.sum(ItemVenda.subtotal).label("total"),
            )
            .join(Produto, Produto.id == ItemVenda.produto_id)
            .join(Venda, Venda.id == ItemVenda.venda_id)
            .filter(Venda.data_venda >= start_dt, Venda.data_venda <= end_dt)
            .group_by(Produto.nome)
            .order_by(func.sum(ItemVenda.quantidade).desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "produto": r.produto,
                "quantidade": int(r.qtd or 0),
                "total_vendido": float(r.total or 0.0),
            }
            for r in rows
        ]

    def _build_estoque_baixo(self, limit: int = 10) -> list[dict]:
        """Retorna produtos com quantidade igual/abaixo do mínimo para ação imediata."""
        settings = load_settings()
        minimo_global = int(settings.get("estoque_minimo_padrao", 5))
        produtos = db_session.query(Produto).all()

        low_items = []
        for p in produtos:
            minimo = int(p.estoque_minimo or minimo_global)
            if int(p.quantidade or 0) <= minimo:
                low_items.append(
                    {
                        "produto": p.nome,
                        "quantidade_atual": int(p.quantidade or 0),
                        "estoque_minimo": minimo,
                    }
                )

        low_items.sort(key=lambda x: (x["quantidade_atual"] - x["estoque_minimo"]))
        return low_items[:limit]

    def _build_fiado_data(self, limit: int = 5) -> dict:
        """Consolida visão de fiado: total, quantidade de devedores e ranking de maiores dívidas."""
        total = (
            db_session.query(func.sum(Cliente.divida_atual))
            .filter(Cliente.divida_atual > 0)
            .scalar()
            or 0.0
        )
        qtd = (
            db_session.query(func.count(Cliente.id))
            .filter(Cliente.divida_atual > 0)
            .scalar()
            or 0
        )
        top_rows = (
            db_session.query(Cliente)
            .filter(Cliente.divida_atual > 0)
            .order_by(Cliente.divida_atual.desc())
            .limit(limit)
            .all()
        )

        return {
            "total": float(total),
            "qtd_clientes": int(qtd),
            "top_clientes": [
                {
                    "nome": c.nome,
                    "telefone": c.telefone or "---",
                    "divida": float(c.divida_atual or 0.0),
                }
                for c in top_rows
            ],
        }

    def _build_recent_movements(self, limit: int = 10) -> list[dict]:
        """Retorna as movimentações financeiras mais recentes (sem VENDA_FIADO por padrão)."""
        rows = (
            db_session.query(FluxoCaixa)
            .filter(FluxoCaixa.tipo != "VENDA_FIADO")
            .order_by(FluxoCaixa.data_registro.desc())
            .limit(limit)
            .all()
        )
        data = []
        for m in rows:
            tipo = m.tipo
            if tipo == "ENTRADA":
                tipo_label = "Entrada"
            elif tipo == "SAIDA":
                tipo_label = "Saída"
            elif tipo == "ABERTURA_CAIXA":
                tipo_label = "Abertura Caixa"
            elif tipo == "FECHAMENTO_CAIXA":
                tipo_label = "Fechamento Caixa"
            else:
                tipo_label = tipo
            data.append(
                {
                    "data": m.data_registro,
                    "tipo": tipo_label,
                    "descricao": m.descricao or "---",
                    "valor": float(m.valor or 0.0),
                }
            )
        return data
