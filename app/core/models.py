from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class CaixaSessao(Base):
    """Sessão de caixa (abertura/fechamento) para consolidação operacional e auditoria."""
    __tablename__ = 'caixa_sessoes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    aberta_em = Column(DateTime, default=datetime.now)
    fechada_em = Column(DateTime, nullable=True)

    valor_abertura = Column(Float, default=0.0)
    valor_contado = Column(Float, nullable=True)
    saldo_esperado = Column(Float, nullable=True)
    diferenca = Column(Float, nullable=True)

    status = Column(String(10), default="ABERTO")  # ABERTO | FECHADO
    observacao = Column(String(200), nullable=True)

    movimentacoes = relationship("FluxoCaixa", back_populates="caixa_sessao")
    vendas = relationship("Venda", back_populates="caixa_sessao")

class Produto(Base):
    """Modelo para representar produtos no estoque."""
    __tablename__ = 'produtos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(20), unique=True, nullable=False)
    nome = Column(String(100), nullable=False)
    preco = Column(Float, nullable=False)
    quantidade = Column(Integer, default=0)
    estoque_minimo = Column(Integer, default=5)
    categoria = Column(String(50))
    criado_em = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Produto(codigo='{self.codigo}', nome='{self.nome}', preco={self.preco})>"

class Cliente(Base):
    """Modelo para representar clientes (módulo fiado)."""
    __tablename__ = 'clientes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    telefone = Column(String(20))
    email = Column(String(100))
    divida_atual = Column(Float, default=0.0)
    criado_em = Column(DateTime, default=datetime.now)

    fiados = relationship("Fiado", back_populates="cliente")

    def __repr__(self):
        return f"<Cliente(nome='{self.nome}', divida={self.divida_atual})>"

class Venda(Base):
    """Modelo para representar uma venda no caixa."""
    __tablename__ = 'vendas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    data_venda = Column(DateTime, default=datetime.now)
    total = Column(Float, nullable=False)
    metodo_pagamento = Column(String(20)) # Dinheiro, Cartão, Pix, Fiado
    caixa_aberto_id = Column(Integer, ForeignKey('fluxo_caixa.id'))
    caixa_sessao_id = Column(Integer, ForeignKey('caixa_sessoes.id'), nullable=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=True)
    cliente_nome = Column(String(100), nullable=True) # Para histórico caso cliente seja deletado

    itens = relationship("ItemVenda", back_populates="venda")
    cliente = relationship("Cliente")
    caixa_sessao = relationship("CaixaSessao", back_populates="vendas")

class ItemVenda(Base):
    """Modelo para representar itens de uma venda."""
    __tablename__ = 'itens_venda'

    id = Column(Integer, primary_key=True, autoincrement=True)
    venda_id = Column(Integer, ForeignKey('vendas.id'))
    produto_id = Column(Integer, ForeignKey('produtos.id'))
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    venda = relationship("Venda", back_populates="itens")
    produto = relationship("Produto")

class Fiado(Base):
    """Modelo para representar registros de fiado (compras e pagamentos)."""
    __tablename__ = 'fiados'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    valor = Column(Float, nullable=False)
    tipo = Column(String(10)) # 'DEBITO' (compra) ou 'CREDITO' (pagamento)
    descricao = Column(String(200))
    data_registro = Column(DateTime, default=datetime.now)

    cliente = relationship("Cliente", back_populates="fiados")

class TipoDespesa(Base):
    """Modelo para representar tipos/categorias de despesas."""
    __tablename__ = 'tipos_despesa'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False, unique=True)
    descricao = Column(String(255))
    ativo = Column(Integer, default=1) # 1 para Ativo, 0 para Inativo
    data_criacao = Column(DateTime, default=datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    movimentacoes = relationship("FluxoCaixa", back_populates="categoria_despesa")

    def __repr__(self):
        return f"<TipoDespesa(nome='{self.nome}', ativo={self.ativo})>"

class FluxoCaixa(Base):
    """Modelo para representar o fluxo de caixa (entradas, saídas e sessões de caixa)."""
    __tablename__ = 'fluxo_caixa'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String(20)) # 'ENTRADA', 'SAIDA', 'ABERTURA_CAIXA', 'FECHAMENTO_CAIXA'
    valor = Column(Float, nullable=False)
    descricao = Column(String(200))
    data_registro = Column(DateTime, default=datetime.now)
    saldo_momento = Column(Float)
    caixa_sessao_id = Column(Integer, ForeignKey('caixa_sessoes.id'), nullable=True)
    
    # Vínculo com categoria de despesa (opcional, usado apenas em SAIDAs)
    tipo_despesa_id = Column(Integer, ForeignKey('tipos_despesa.id'), nullable=True)
    categoria_despesa = relationship("TipoDespesa", back_populates="movimentacoes")
    caixa_sessao = relationship("CaixaSessao", back_populates="movimentacoes")

    def __repr__(self):
        return f"<FluxoCaixa(tipo='{self.tipo}', valor={self.valor}, data={self.data_registro})>"
