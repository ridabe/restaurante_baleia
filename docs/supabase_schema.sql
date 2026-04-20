
CREATE TABLE caixa_sessoes (
	id SERIAL NOT NULL, 
	aberta_em TIMESTAMP WITHOUT TIME ZONE, 
	fechada_em TIMESTAMP WITHOUT TIME ZONE, 
	valor_abertura FLOAT, 
	valor_contado FLOAT, 
	saldo_esperado FLOAT, 
	diferenca FLOAT, 
	status VARCHAR(10), 
	observacao VARCHAR(200), 
	PRIMARY KEY (id)
)

;


CREATE TABLE clientes (
	id SERIAL NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	telefone VARCHAR(20), 
	email VARCHAR(100), 
	divida_atual FLOAT, 
	criado_em TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
)

;


CREATE TABLE produtos (
	id SERIAL NOT NULL, 
	codigo VARCHAR(20) NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	preco FLOAT NOT NULL, 
	quantidade INTEGER, 
	estoque_minimo INTEGER, 
	categoria VARCHAR(50), 
	criado_em TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (codigo)
)

;


CREATE TABLE tipos_despesa (
	id SERIAL NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	descricao VARCHAR(255), 
	ativo INTEGER, 
	data_criacao TIMESTAMP WITHOUT TIME ZONE, 
	data_atualizacao TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (nome)
)

;


CREATE TABLE fiados (
	id SERIAL NOT NULL, 
	cliente_id INTEGER, 
	valor FLOAT NOT NULL, 
	tipo VARCHAR(10), 
	descricao VARCHAR(200), 
	data_registro TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(cliente_id) REFERENCES clientes (id)
)

;


CREATE TABLE fluxo_caixa (
	id SERIAL NOT NULL, 
	tipo VARCHAR(20), 
	meio_pagamento VARCHAR(20), 
	valor FLOAT NOT NULL, 
	descricao VARCHAR(200), 
	data_registro TIMESTAMP WITHOUT TIME ZONE, 
	saldo_momento FLOAT, 
	caixa_sessao_id INTEGER, 
	tipo_despesa_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(caixa_sessao_id) REFERENCES caixa_sessoes (id), 
	FOREIGN KEY(tipo_despesa_id) REFERENCES tipos_despesa (id)
)

;


CREATE TABLE vendas (
	id SERIAL NOT NULL, 
	data_venda TIMESTAMP WITHOUT TIME ZONE, 
	total FLOAT NOT NULL, 
	metodo_pagamento VARCHAR(20), 
	caixa_aberto_id INTEGER, 
	caixa_sessao_id INTEGER, 
	cliente_id INTEGER, 
	cliente_nome VARCHAR(100), 
	PRIMARY KEY (id), 
	FOREIGN KEY(caixa_aberto_id) REFERENCES fluxo_caixa (id), 
	FOREIGN KEY(caixa_sessao_id) REFERENCES caixa_sessoes (id), 
	FOREIGN KEY(cliente_id) REFERENCES clientes (id)
)

;


CREATE TABLE itens_venda (
	id SERIAL NOT NULL, 
	venda_id INTEGER, 
	produto_id INTEGER, 
	quantidade INTEGER NOT NULL, 
	preco_unitario FLOAT NOT NULL, 
	subtotal FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(venda_id) REFERENCES vendas (id), 
	FOREIGN KEY(produto_id) REFERENCES produtos (id)
)

;
