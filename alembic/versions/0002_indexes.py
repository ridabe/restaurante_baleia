from alembic import op

revision = "0002_indexes"
down_revision = "0001_baseline"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("create index if not exists idx_fluxo_caixa_data on fluxo_caixa (data_registro)")
    op.execute("create index if not exists idx_fluxo_caixa_tipo on fluxo_caixa (tipo)")
    op.execute("create index if not exists idx_fluxo_caixa_meio on fluxo_caixa (meio_pagamento)")
    op.execute("create index if not exists idx_fluxo_caixa_sessao on fluxo_caixa (caixa_sessao_id)")
    op.execute("create index if not exists idx_fluxo_caixa_despesa on fluxo_caixa (tipo_despesa_id)")

    op.execute("create index if not exists idx_vendas_data on vendas (data_venda)")
    op.execute("create index if not exists idx_vendas_cliente on vendas (cliente_id)")
    op.execute("create index if not exists idx_vendas_sessao on vendas (caixa_sessao_id)")

    op.execute("create index if not exists idx_itens_venda_venda on itens_venda (venda_id)")
    op.execute("create index if not exists idx_itens_venda_produto on itens_venda (produto_id)")

    op.execute("create index if not exists idx_fiados_cliente on fiados (cliente_id)")
    op.execute("create index if not exists idx_fiados_data on fiados (data_registro)")

    op.execute("create index if not exists idx_clientes_divida on clientes (divida_atual)")


def downgrade():
    op.execute("drop index if exists idx_clientes_divida")
    op.execute("drop index if exists idx_fiados_data")
    op.execute("drop index if exists idx_fiados_cliente")
    op.execute("drop index if exists idx_itens_venda_produto")
    op.execute("drop index if exists idx_itens_venda_venda")
    op.execute("drop index if exists idx_vendas_sessao")
    op.execute("drop index if exists idx_vendas_cliente")
    op.execute("drop index if exists idx_vendas_data")
    op.execute("drop index if exists idx_fluxo_caixa_despesa")
    op.execute("drop index if exists idx_fluxo_caixa_sessao")
    op.execute("drop index if exists idx_fluxo_caixa_meio")
    op.execute("drop index if exists idx_fluxo_caixa_tipo")
    op.execute("drop index if exists idx_fluxo_caixa_data")

