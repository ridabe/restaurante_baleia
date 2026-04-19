import logging
from datetime import datetime
from app.core.database import db_session
from app.core.models import Venda, ItemVenda, Produto, FluxoCaixa, Cliente

logger = logging.getLogger('CaixaService')

class CaixaService:
    """Serviço para gerenciar vendas e sessões de caixa."""

    @staticmethod
    def registrar_venda(itens_venda, metodo_pagamento, cliente_id=None, cliente_nome=None):
        """
        Registra uma venda, atualiza o estoque e o fluxo de caixa.
        itens_venda: lista de dicts [{'produto_id': ID, 'quantidade': QTD, 'preco': PRECO}]
        """
        try:
            total_venda = sum(item['quantidade'] * item['preco'] for item in itens_venda)
            
            # 1. Criar a Venda
            nova_venda = Venda(
                total=total_venda,
                metodo_pagamento=metodo_pagamento,
                cliente_id=cliente_id,
                cliente_nome=cliente_nome
            )
            db_session.add(nova_venda)
            db_session.flush() # Para obter o ID da venda

            # 2. Processar itens, baixar estoque e criar ItemVenda
            itens_resumo = []
            for item in itens_venda:
                produto = db_session.query(Produto).filter(Produto.id == item['produto_id']).first()
                if not produto or produto.quantidade < item['quantidade']:
                    raise Exception(f"Estoque insuficiente para: {produto.nome if produto else 'Desconhecido'}")
                
                itens_resumo.append(f"{item['quantidade']}x {produto.nome}")

                # Baixa estoque
                produto.quantidade -= item['quantidade']
                
                # Cria item da venda
                novo_item = ItemVenda(
                    venda_id=nova_venda.id,
                    produto_id=item['produto_id'],
                    quantidade=item['quantidade'],
                    preco_unitario=item['preco'],
                    subtotal=item['quantidade'] * item['preco']
                )
                db_session.add(novo_item)

            # 3. Se for FIADO, registrar no cliente
            if metodo_pagamento == 'FIADO' and cliente_id:
                cliente = db_session.query(Cliente).filter(Cliente.id == cliente_id).first()
                if cliente:
                    # Registrar no histórico de fiados do cliente
                    # O FiadoService.registrar_fiado já incrementa a dívida do cliente internamente.
                    from app.modules.fiado.service import FiadoService
                    resumo_txt = ", ".join(itens_resumo)
                    desc = (
                        f"Venda #{nova_venda.id} (FIADO) cliente_id={cliente_id} "
                        f"total=R$ {total_venda:.2f} Itens: {resumo_txt}"
                    )
                    FiadoService.registrar_fiado(cliente_id, total_venda, desc[:200])
                else:
                    raise Exception("Cliente não selecionado para venda fiada.")

            # 4. Registrar no Fluxo de Caixa (se não for fiado, pois fiado entra no caixa quando é pago)
            if metodo_pagamento != 'FIADO':
                novo_fluxo = FluxoCaixa(
                    tipo='ENTRADA',
                    valor=total_venda,
                    descricao=f"Venda #{nova_venda.id} ({metodo_pagamento})"
                )
                db_session.add(novo_fluxo)
            else:
                # Registra a venda fiada como movimentação neutra (não altera saldo),
                # para rastreabilidade no histórico do fluxo de caixa.
                novo_fluxo = FluxoCaixa(
                    tipo='VENDA_FIADO',
                    valor=total_venda,
                    descricao=(
                        f"VENDA_FIADO venda_id={nova_venda.id} cliente_id={cliente_id or 0} "
                        f"total={total_venda:.2f} Cliente: {cliente_nome or 'Não informado'}"
                    )[:200]
                )
                db_session.add(novo_fluxo)

            db_session.commit()
            logger.info(f"Venda #{nova_venda.id} registrada com sucesso. Total: R$ {total_venda:.2f}")
            return True, f"Venda #{nova_venda.id} realizada!"
        except Exception as e:
            db_session.rollback()
            logger.error(f"Erro ao registrar venda: {e}")
            return False, f"Erro na venda: {str(e)}"

    @staticmethod
    def abrir_caixa(valor_inicial):
        """Registra a abertura de caixa."""
        try:
            nova_abertura = FluxoCaixa(
                tipo='ABERTURA_CAIXA',
                valor=valor_inicial,
                descricao="Abertura de caixa (Saldo inicial)"
            )
            db_session.add(nova_abertura)
            db_session.commit()
            logger.info(f"Caixa aberto com R$ {valor_inicial:.2f}")
            return True, "Caixa aberto com sucesso."
        except Exception as e:
            db_session.rollback()
            logger.error(f"Erro ao abrir caixa: {e}")
            return False, str(e)

    @staticmethod
    def fechar_caixa():
        """Simula o fechamento de caixa calculando o saldo atual."""
        # Na prática, poderíamos registrar um evento de fechamento
        pass
