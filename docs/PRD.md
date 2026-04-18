# PRD — Bar do Baleia (Sistema de Gestão)

Versão: 1.0  
Data: 2026-04-18  
Produto: Aplicação Desktop (Windows)  
Stack: Python + PySide6 + SQLAlchemy + SQLite

## 1. Visão Geral

O **Bar do Baleia — Sistema de Gestão** é uma aplicação desktop para operação e controle do dia a dia de um bar/restaurante, com foco em:

- **Ponto de venda (Caixa)** com baixa automática de estoque;
- **Controle de clientes e fiado**, incluindo pagamentos e histórico;
- **Fluxo de caixa** com entradas/saídas, categorias de despesas e relatório por período;
- **Gestão de estoque** com alerta de estoque baixo e reposição rápida;
- **Relatórios e documentos** com impressão/PDF e identidade visual padronizada (logo institucional).

O sistema é desenhado para operação local, com banco SQLite e configuração via arquivo JSON, além de suporte a empacotamento em `.exe` via PyInstaller.

## 2. Objetivos

### 2.1 Objetivos de Negócio
- Centralizar operação de vendas e controle financeiro do estabelecimento.
- Reduzir divergências de estoque com baixa automática no momento da venda.
- Permitir gestão de fiado com rastreabilidade (débitos e pagamentos).
- Profissionalizar a apresentação institucional em tickets, relatórios e UI.

### 2.2 Objetivos de Produto
- Interface moderna e consistente entre módulos.
- Operação rápida no balcão (caixa) com busca e atalhos.
- Impressão confiável (impressora térmica/A4/PDF via driver).

## 3. Públicos / Personas
- **Operador(a) de Caixa**: realiza vendas rápidas, precisa de confirmação, ticket e baixa de estoque automática.
- **Gestor(a)**: consulta estoque, fiado e fluxo de caixa; imprime relatórios para conferência.
- **Administrativo**: mantém dados institucionais e parametrizações (logo, observações, etc.).

## 4. Escopo

### 4.1 Dentro do Escopo (MVP atual)
- Dashboard com identidade institucional (logo) e componentes informativos (notícias/versículo).
- Caixa: montagem de pedido, confirmação, registro da venda, impressão/visualização de ticket.
- Estoque: cadastro/edição/remoção de produtos, alerta de estoque baixo, reposição rápida por item, relatório de estoque.
- Fiado: cadastro de clientes, registro de histórico, pagamento de dívida, relatório de clientes/débitos.
- Fluxo de Caixa: visualizar saldo/resumo mensal, registrar entradas e saídas, filtrar por período, relatório por período.
- Tipos de Despesa: CRUD com regra de inativação quando houver vínculos.
- Configurações: dados da empresa (institucionais), logo, rodapé do ticket, observação de relatórios, URL do BRNews.
- Impressão: relatórios e ticket via HTML + QTextDocument + QPrinter, com cabeçalho institucional e logo.

### 4.2 Fora do Escopo (Backlog)
- Autenticação e perfis de acesso.
- Multiempresa / multiusuário.
- Integração fiscal (NFC-e/SAT/CF-e).
- Sincronização em nuvem e multi-dispositivo.
- Indexador/busca avançada de notícias (mencionado no backlog do BRNews).
- Fechamento de caixa completo com conferência (no código existe apenas esqueleto).

## 5. Requisitos Funcionais por Módulo

### 5.1 Navegação / Shell do Sistema
- Sidebar com logo institucional, nome do sistema e subtítulo.
- Páginas:
  - Início (Dashboard)
  - Caixa
  - Estoque
  - Clientes/Fiado
  - Fluxo de Caixa
  - Tipos de Despesas
  - Configurações

### 5.2 Dashboard (Início)
Funcionalidades:
- Exibir logo e identidade institucional.
- Exibir notícias com atualização periódica.
  - Provider primário: BRNews `/v1/news/`.
  - Fallback: RSS (Google News BR) quando BRNews estiver indisponível.
- Atualização automática por intervalo configurável.
- Exibir versículo bíblico na sidebar (atualização periódica).

Regras/observações:
- A área de notícias não pode travar a UI; deve operar de forma assíncrona.
- Links de notícia devem abrir no navegador.

### 5.3 Caixa (PDV)
Funcionalidades:
- Busca de produto por nome/código.
- Montagem do pedido com itens e quantidades.
- Exibir total e permitir seleção de forma de pagamento: Dinheiro, Cartão, Pix, FIADO.
- Para FIADO: exigir seleção de cliente.
- Gerar ticket “Documento Não Fiscal” com cabeçalho institucional e logo.

Regras de negócio:
- Ao registrar venda:
  - Calcular `total_venda` por soma de subtotais.
  - Criar `Venda` e `ItemVenda`.
  - Baixar estoque (`Produto.quantidade -= quantidade_vendida`).
  - Se método **FIADO**:
    - Registrar um débito em `Fiado` para o cliente e incrementar `Cliente.divida_atual`.
    - Não registrar entrada no fluxo de caixa (o dinheiro entra quando o cliente paga).
  - Se método **não FIADO**:
    - Registrar `FluxoCaixa(tipo='ENTRADA')` com descrição “Venda #ID (método)”.

### 5.4 Estoque
Funcionalidades:
- Cadastrar/editar/remover produtos (código único, nome, preço, quantidade, estoque mínimo).
- Busca por nome/código na tabela.
- Destaque visual de itens com estoque baixo.
- Banner discreto quando existir item com `quantidade < estoque_minimo`.
- Ação por item com `quantidade <= estoque_minimo`: botão “Atualizar” abre diálogo para inserir nova quantidade.
- Relatório de estoque para impressão/PDF com cabeçalho institucional e logo.

Regras de negócio:
- `Produto.codigo` deve ser único.
- Estoque baixo:
  - “Abaixo do mínimo” quando `quantidade < estoque_minimo` (alerta/banner).
  - “Atenção” quando `quantidade <= estoque_minimo` (habilita ação de reposição).

### 5.5 Clientes / Fiado
Funcionalidades:
- Cadastro de cliente (nome obrigatório).
- Exibir lista com dívida atual e estatísticas.
- Abrir histórico detalhado (débitos/créditos) por cliente.
- Registrar pagamento (crédito) e reduzir dívida.
- Imprimir relatório de clientes/débitos com cabeçalho institucional e logo.

Regras de negócio:
- Compra fiada gera `Fiado(tipo='DEBITO')` e incrementa `Cliente.divida_atual`.
- Pagamento gera `Fiado(tipo='CREDITO')`, decrementa `Cliente.divida_atual` e registra `FluxoCaixa(tipo='ENTRADA')`.
- Excluir cliente remove também seus registros de fiado.

### 5.6 Fluxo de Caixa
Funcionalidades:
- Exibir saldo atual (entradas - saídas).
- Exibir resumo mensal: total de entradas, total de saídas e saldo do mês.
- Registrar:
  - Entrada extra (`FluxoCaixa.tipo='ENTRADA'`)
  - Saída/despesa (`FluxoCaixa.tipo='SAIDA'`) associando categoria quando aplicável
- Filtrar histórico por período (data inicial e final).
- Imprimir relatório do período com cabeçalho institucional e logo.

Regras de negócio:
- Saldo atual:
  - Entradas consideradas: `ENTRADA`, `ABERTURA_CAIXA`
  - Saídas consideradas: `SAIDA`, `FECHAMENTO_CAIXA`
- Saída pode vincular `tipo_despesa_id` (categoria).

### 5.7 Tipos de Despesa (Categorias)
Funcionalidades:
- Criar/editar categorias de despesa.
- Ativar/inativar categoria.
- Excluir categoria:
  - Se houver vínculos com movimentações (FluxoCaixa), inativar ao invés de excluir.

Regras de negócio:
- Nome é obrigatório e único (validação case-insensitive).
- Exclusão com vínculos preserva histórico (inativação).

### 5.8 Configurações
Funcionalidades:
- Manter dados institucionais (nome fantasia, razão social, CNPJ, telefone, e-mail, endereço).
- Definir:
  - `empresa_logo_path` (logo institucional)
  - `ticket_rodape`
  - `relatorio_observacao`
  - `brnews_base_url` (fonte primária de notícias)

## 6. Relatórios, Tickets e Documentos Não Fiscais

### 6.1 Padrão de Cabeçalho
Todos relatórios impressos/PDF devem conter:
- Logo institucional (tamanho reduzido e proporcional)
- Nome da empresa e dados institucionais
- Título do relatório
- Período (quando aplicável)
- Data/hora de emissão

### 6.2 Ticket do Caixa
O ticket deve conter:
- Logo em tamanho de ícone no topo
- Nome da empresa e dados (CNPJ, telefone, endereço)
- Data/hora e cliente
- Itens com quantidade, unitário e subtotal
- Total e rodapé
- Texto “DOCUMENTO NÃO FISCAL”

### 6.3 Compatibilidade de Impressão e Empacotamento
- Impressão via `QTextDocument` + `QPrinter`.
- Logo inserido no HTML via URI absoluta (`file:///...`) para evitar falha de caminho relativo.
- Resolução de assets compatível com PyInstaller via `resource_path` e `_MEIPASS`.

## 7. Modelo de Dados (Entidades)

Entidades principais (SQLAlchemy):
- **Produto**: estoque, preço, mínimo
- **Cliente**: dados e `divida_atual`
- **Fiado**: registros de débito/crédito por cliente
- **Venda**: total e método, vínculo opcional com cliente
- **ItemVenda**: itens por venda
- **FluxoCaixa**: entradas/saídas e eventos de caixa
- **TipoDespesa**: categorias para saídas

Banco de dados:
- SQLite local: `database.db` no diretório de execução.

## 8. Requisitos Não Funcionais

- **Performance**: UI responsiva; buscas e listas devem carregar rapidamente em base local.
- **Confiabilidade**: operações críticas (venda/pagamento) devem ser transacionais (commit/rollback).
- **Portabilidade**: rodar em Windows; suporte a empacotamento em `.exe`.
- **Observabilidade**: logs em `logs/` (app e database).
- **Segurança**: sem armazenamento de credenciais sensíveis; dados locais e sem autenticação no MVP.

## 9. Dependências e Integrações Externas
- Bible API (`bible-api.com`) para versículo (sem chave).
- BRNews (API externa/auto-hospedada) para notícias do Brasil (configurável).
- RSS público como fallback (Google News BR).

## 10. Critérios de Aceite (Amostra)
- Registrar venda baixa estoque e cria registros de venda e itens.
- Venda FIADO exige cliente e cria débito no fiado; não cria entrada no fluxo.
- Pagamento de dívida cria crédito no fiado e entrada no fluxo.
- Relatórios e ticket imprimem com logo institucional em tamanho apropriado.
- Estoque exibe ação “Atualizar” por item quando `quantidade <= mínimo`.
- Dashboard carrega notícias via BRNews ou fallback RSS sem travar a interface.

## 11. Riscos e Mitigações
- Falha de rede (notícias/versículo): fallback e tolerância a erro sem travar UI.
- Impressão/PDF: diferenças entre drivers; manter HTML simples e usar URIs absolutas.
- Empacotamento: garantir assets via `--add-data` e `resource_path`.

## 12. Backlog Recomendado
- Fechamento de caixa real (conferência, sangria, relatórios).
- Auditoria de alterações (estoque/preço).
- Perfil de usuário e permissões.
- Exportação CSV/Excel.
- Multiempresa e logotipo customizado por empresa.
