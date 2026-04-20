import os
import random
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"), override=False)
except Exception:
    pass

from app.core.config import init_config
from app.core.database import db_session, init_db
from app.core.models import CaixaSessao, Cliente, Fiado, FluxoCaixa, ItemVenda, Produto, TipoDespesa, Venda


def money(v: float) -> float:
    return float(f"{v:.2f}")


def now_minus_days(days: int, hour: int, minute: int) -> datetime:
    base = datetime.now() - timedelta(days=days)
    return base.replace(hour=hour, minute=minute, second=0, microsecond=0)


def reset_data():
    db_session.query(ItemVenda).delete()
    db_session.query(Venda).delete()
    db_session.query(Fiado).delete()
    db_session.query(FluxoCaixa).delete()
    db_session.query(CaixaSessao).delete()
    db_session.query(Produto).delete()
    db_session.query(Cliente).delete()
    db_session.commit()


def has_any_data() -> bool:
    return db_session.query(Produto).count() > 0 or db_session.query(Cliente).count() > 0


def create_products():
    produtos = []
    base = [
        ("101", "Cerveja 600ml", 12.0, 80, 10),
        ("102", "Cerveja Long Neck", 9.0, 120, 15),
        ("201", "Refrigerante Lata", 6.0, 60, 10),
        ("202", "Água 500ml", 4.0, 90, 12),
        ("301", "Porção Batata", 35.0, 20, 5),
        ("302", "Porção Calabresa", 42.0, 18, 5),
        ("303", "Porção Frango", 45.0, 16, 5),
        ("401", "Feijoada", 35.0, 25, 6),
        ("402", "Prato Executivo", 28.0, 30, 8),
        ("403", "Hambúrguer", 24.0, 35, 10),
        ("501", "Caipirinha", 22.0, 40, 8),
        ("502", "Gin Tônica", 28.0, 30, 6),
        ("503", "Dose Whisky", 18.0, 25, 5),
    ]
    for codigo, nome, preco, qtd, minimo in base:
        p = Produto(codigo=codigo, nome=nome, preco=money(preco), quantidade=qtd, estoque_minimo=minimo)
        db_session.add(p)
        produtos.append(p)
    db_session.flush()
    return produtos


def create_clients():
    nomes = [
        ("Ricardo", "(11) 90000-0001"),
        ("Juliana", "(11) 90000-0002"),
        ("Marcos", "(11) 90000-0003"),
        ("Fernanda", "(11) 90000-0004"),
        ("Bruno", "(11) 90000-0005"),
        ("Camila", "(11) 90000-0006"),
        ("Diego", "(11) 90000-0007"),
        ("Patrícia", "(11) 90000-0008"),
    ]
    clientes = []
    for nome, tel in nomes:
        c = Cliente(nome=nome, telefone=tel, email=f"{nome.lower()}@exemplo.com")
        db_session.add(c)
        clientes.append(c)
    db_session.flush()
    return clientes


def get_categorias():
    cats = db_session.query(TipoDespesa).order_by(TipoDespesa.nome.asc()).all()
    return cats


def add_fluxo(
    *,
    tipo: str,
    valor: float,
    descricao: str,
    data_registro: datetime,
    caixa_sessao_id: int | None,
    meio_pagamento: str | None = None,
    tipo_despesa_id: int | None = None,
):
    m = FluxoCaixa(
        tipo=tipo,
        valor=money(valor),
        descricao=(descricao or "")[:200],
        data_registro=data_registro,
        caixa_sessao_id=caixa_sessao_id,
        meio_pagamento=meio_pagamento,
        tipo_despesa_id=tipo_despesa_id,
    )
    db_session.add(m)
    return m


def add_venda(
    *,
    data_venda: datetime,
    metodo: str,
    itens: list[tuple[Produto, int]],
    caixa_sessao_id: int | None,
    cliente: Cliente | None = None,
):
    total = sum(p.preco * qtd for p, qtd in itens)
    v = Venda(
        data_venda=data_venda,
        total=money(total),
        metodo_pagamento=metodo,
        caixa_sessao_id=caixa_sessao_id,
        cliente_id=cliente.id if cliente else None,
        cliente_nome=cliente.nome if cliente else None,
    )
    db_session.add(v)
    db_session.flush()

    for p, qtd in itens:
        it = ItemVenda(
            venda_id=v.id,
            produto_id=p.id,
            quantidade=qtd,
            preco_unitario=money(p.preco),
            subtotal=money(p.preco * qtd),
        )
        db_session.add(it)
        p.quantidade = int(p.quantidade or 0) - int(qtd)

    if metodo != "FIADO":
        meio = "OUTROS"
        if metodo.upper() == "DINHEIRO":
            meio = "DINHEIRO"
        elif metodo.upper() == "PIX":
            meio = "PIX"
        elif metodo.upper() in ("CARTAO", "CARTÃO"):
            meio = "CARTAO"

        add_fluxo(
            tipo="ENTRADA",
            valor=total,
            descricao=f"Venda #{v.id} ({metodo})",
            data_registro=data_venda,
            caixa_sessao_id=caixa_sessao_id,
            meio_pagamento=meio,
        )
    else:
        add_fluxo(
            tipo="VENDA_FIADO",
            valor=total,
            descricao=f"VENDA_FIADO venda_id={v.id} cliente_id={cliente.id if cliente else 0} total={money(total):.2f} Cliente: {cliente.nome if cliente else 'Não informado'}",
            data_registro=data_venda,
            caixa_sessao_id=caixa_sessao_id,
            meio_pagamento="FIADO",
        )
        if cliente:
            db_session.add(
                Fiado(
                    cliente_id=cliente.id,
                    valor=money(total),
                    tipo="DEBITO",
                    descricao=f"Venda #{v.id} (FIADO)",
                    data_registro=data_venda,
                )
            )
            cliente.divida_atual = money(float(cliente.divida_atual or 0.0) + float(total))

    return v


def add_pagamento_fiado(
    *,
    cliente: Cliente,
    valor: float,
    data: datetime,
    meio: str,
    caixa_sessao_id: int | None,
):
    pago = money(valor)
    cliente.divida_atual = money(max(0.0, float(cliente.divida_atual or 0.0) - float(pago)))
    db_session.add(
        Fiado(
            cliente_id=cliente.id,
            valor=pago,
            tipo="CREDITO",
            descricao=f"Pagamento ({meio})",
            data_registro=data,
        )
    )
    add_fluxo(
        tipo="ENTRADA",
        valor=pago,
        descricao=f"Pagamento de dívida | Cliente: {cliente.nome} | Pago: R$ {pago:.2f}",
        data_registro=data,
        caixa_sessao_id=caixa_sessao_id,
        meio_pagamento=meio,
    )


def compute_expected_cash(sessao_id: int, abertura: float) -> float:
    entradas = (
        db_session.query(FluxoCaixa)
        .filter(
            FluxoCaixa.caixa_sessao_id == sessao_id,
            FluxoCaixa.tipo == "ENTRADA",
            FluxoCaixa.meio_pagamento == "DINHEIRO",
        )
        .all()
    )
    saidas = (
        db_session.query(FluxoCaixa)
        .filter(
            FluxoCaixa.caixa_sessao_id == sessao_id,
            FluxoCaixa.tipo == "SAIDA",
            FluxoCaixa.meio_pagamento == "DINHEIRO",
        )
        .all()
    )
    total_in = sum(float(m.valor or 0.0) for m in entradas)
    total_out = sum(float(m.valor or 0.0) for m in saidas)
    return money(float(abertura) + total_in - total_out)


def seed():
    random.seed(42)

    produtos = create_products()
    clientes = create_clients()
    categorias = get_categorias()

    sessions = []
    for days_ago in (2, 1, 0):
        opened = now_minus_days(days_ago, 10, 0)
        closed = None if days_ago == 0 else now_minus_days(days_ago, 22, 0)
        sess = CaixaSessao(
            aberta_em=opened,
            fechada_em=closed,
            valor_abertura=money(200.0),
            status="ABERTO" if days_ago == 0 else "FECHADO",
            observacao="Sessão de teste",
        )
        db_session.add(sess)
        db_session.flush()
        sessions.append(sess)

        add_fluxo(
            tipo="ABERTURA_CAIXA",
            valor=200.0,
            descricao=f"Abertura de caixa (Sessão #{sess.id})",
            data_registro=opened,
            caixa_sessao_id=sess.id,
            meio_pagamento="DINHEIRO",
        )

        for _ in range(8 if days_ago else 6):
            metodo = random.choice(["DINHEIRO", "PIX", "CARTAO", "DINHEIRO", "PIX"])
            hora = random.choice([11, 12, 13, 18, 19, 20, 21])
            minuto = random.choice([0, 10, 20, 30, 40, 50])
            dt = now_minus_days(days_ago, hora, minuto)

            itens = []
            for __ in range(random.choice([1, 1, 2, 2, 3])):
                p = random.choice(produtos)
                qtd = random.choice([1, 1, 2, 3])
                itens.append((p, qtd))

            add_venda(data_venda=dt, metodo=metodo, itens=itens, caixa_sessao_id=sess.id)

        for _ in range(3):
            cli = random.choice(clientes)
            hora = random.choice([12, 13, 19, 20, 21])
            minuto = random.choice([5, 15, 25, 35, 45, 55])
            dt = now_minus_days(days_ago, hora, minuto)
            itens = [(random.choice(produtos), random.choice([1, 2])) for __ in range(2)]
            add_venda(data_venda=dt, metodo="FIADO", itens=itens, caixa_sessao_id=sess.id, cliente=cli)

        for _ in range(3):
            cat = random.choice(categorias) if categorias else None
            valor = random.choice([15, 25, 35, 50, 60])
            hora = random.choice([14, 16, 17, 21])
            dt = now_minus_days(days_ago, hora, 10)
            add_fluxo(
                tipo="SAIDA",
                valor=valor,
                descricao=f"[{cat.nome if cat else 'Sem categoria'}] Compra/Despesa teste",
                data_registro=dt,
                caixa_sessao_id=sess.id,
                meio_pagamento="DINHEIRO",
                tipo_despesa_id=cat.id if cat else None,
            )

        if days_ago != 0:
            expected = compute_expected_cash(sess.id, 200.0)
            sess.saldo_esperado = expected
            sess.valor_contado = expected
            sess.diferenca = 0.0
            add_fluxo(
                tipo="FECHAMENTO_CAIXA",
                valor=0.0,
                descricao=f"Fechamento de caixa (Sessão #{sess.id}) | Esperado: R$ {expected:.2f} | Contado: R$ {expected:.2f} | Diferença: R$ 0.00",
                data_registro=closed,
                caixa_sessao_id=sess.id,
                meio_pagamento="DINHEIRO",
            )

    open_sess = sessions[-1]
    debtors = [c for c in clientes if float(c.divida_atual or 0.0) > 0.0]
    for cli in debtors[:4]:
        paid = money(min(float(cli.divida_atual), random.choice([20, 30, 50])))
        if paid <= 0:
            continue
        meio = random.choice(["DINHEIRO", "PIX", "CARTAO"])
        dt = now_minus_days(0, 21, random.choice([5, 20, 35, 50]))
        add_pagamento_fiado(cliente=cli, valor=paid, data=dt, meio=meio, caixa_sessao_id=open_sess.id)

    db_session.commit()


def main():
    init_config()
    init_db()

    force = "--force" in sys.argv
    reset = "--reset" in sys.argv
    if reset:
        reset_data()
    elif has_any_data() and not force:
        raise SystemExit("Banco já possui dados. Use --force para adicionar mesmo assim ou --reset para limpar.")

    seed()
    print("OK: dados fake inseridos.")


if __name__ == "__main__":
    main()

