# Guia de Uso — Bar do Baleia (Sistema de Gestão)

Este guia descreve como operar cada módulo do sistema, com exemplos práticos, boas práticas e efeitos esperados no estoque/fiado/fluxo de caixa.

## 1. Primeiros Passos

### 1.1 Executar em desenvolvimento
- Execute `python main.py`
- O sistema cria automaticamente (se não existirem):
  - `database.db` (SQLite)
  - `config/settings.json`
  - pastas: `logs/`, `config/`, `relatorios/`

Arquivos e pontos relevantes:
- Inicialização: [main.py](file:///c:/Projetos/baleia/main.py)
- Banco e criação de tabelas: [database.py](file:///c:/Projetos/baleia/app/core/database.py)
- Configurações: [config.py](file:///c:/Projetos/baleia/app/core/config.py)

### 1.2 Executável (.exe)
- Build: [build.py](file:///c:/Projetos/baleia/build.py)
- O build inclui a pasta `app/` via `--add-data=app;app`.
- Opcional: se existir `app/img/logo_baleia.ico`, o build utiliza como ícone nativo.

## 2. Navegação do Sistema

A navegação é feita pela sidebar:
- Início (Dashboard)
- Caixa
- Estoque
- Clientes / Fiado
- Fluxo de Caixa
- Tipos de Despesas
- Configurações

Shell principal: [main_window.py](file:///c:/Projetos/baleia/app/ui/main_window.py)

## 3. Dashboard (Início)

### 3.1 Objetivo
Exibir identidade institucional e informações rápidas:
- Logo e nome do sistema
- Notícias do Brasil (BRNews com fallback RSS)

Implementação: [dashboard_widget.py](file:///c:/Projetos/baleia/app/ui/dashboard_widget.py)

### 3.2 Notícias (BRNews / RSS)
O painel tenta buscar notícias em:
1. **BRNews** (`brnews_base_url` + `/v1/news/`)
2. Se falhar: **RSS** (fallback)

Configurações relacionadas:
- `brnews_base_url`
- `news_refresh_interval_sec`
- `news_max_items`
- `news_rss_fallback_url`

Widget: [news_widget.py](file:///c:/Projetos/baleia/app/ui/news_widget.py)

Exemplo:
- BRNews rodando em WSL: `http://172.23.0.2:5000`
- BRNews local: `http://127.0.0.1:5000`

## 4. Caixa (Ponto de Venda)

### 4.1 Fluxo básico de venda
1. Vá em **Caixa**.
2. Em “Adicionar Itens ao Pedido”, busque por:
   - Nome do produto (parcial) ou
   - Código do produto (exato)
3. Ajuste a quantidade (Qtd) e clique **+ ADICIONAR ITEM**.
4. Repita para todos os itens.
5. Clique **CONFIRMAR**.
6. Confira a “Prévia do Ticket”.
7. Clique **RECEBER PAGAMENTO** para persistir a venda.

### 4.2 Exemplo (pagamento Dinheiro)
Pedido:
- Produto: `101 - Cerveja 600ml` (Qtd 2, R$ 12,00)
- Produto: `205 - Porção de Batata` (Qtd 1, R$ 35,00)

Resultado esperado:
- Venda criada com total R$ 59,00
- Estoque baixado automaticamente (Produto.quantidade diminui)
- Fluxo de caixa registra uma **ENTRADA** com descrição “Venda #ID (Dinheiro)”

Regras de negócio do registro de venda: [caixa/service.py](file:///c:/Projetos/baleia/app/modules/caixa/service.py#L11-L75)

### 4.3 Venda FIADO (obrigatório selecionar cliente)
1. Cadastre/garanta o cliente no módulo **Clientes / Fiado**.
2. No **Caixa**, selecione método **FIADO**.
3. Selecione o cliente.
4. Confirme e receba.

Resultado esperado:
- Cria débito no fiado do cliente (`Fiado.tipo = 'DEBITO'`)
- Incrementa `Cliente.divida_atual`
- **Não** registra entrada no fluxo de caixa (entra quando o cliente pagar)

### 4.4 Ticket / Documento Não Fiscal
- O ticket é exibido em HTML e inclui logo no topo.
- Rodapé configurável via `ticket_rodape`.

Cabeçalho do ticket: [branding.py](file:///c:/Projetos/baleia/app/core/branding.py#L99-L110)  
Geração da prévia: [caixa/ui.py](file:///c:/Projetos/baleia/app/modules/caixa/ui.py#L277-L303)

## 5. Estoque

### 5.1 Cadastrar produto
1. Vá em **Estoque**.
2. Clique **+ Adicionar Produto**.
3. Preencha:
   - Código (único)
   - Nome
   - Preço
   - Quantidade inicial
   - Estoque mínimo
4. Salve.

### 5.2 Editar produto
Opções:
- Duplo clique na linha
- Botão “Editar Selecionado”

### 5.3 Alerta de estoque baixo e reposição
Regras:
- **Banner** é exibido quando existe item com `quantidade < estoque_minimo`.
- **Botão “Atualizar” por item** aparece quando `quantidade <= estoque_minimo`.

Como repor:
1. Localize o item com destaque vermelho.
2. Na coluna **Ações**, clique **Atualizar**.
3. Informe a nova quantidade e confirme.

Isso atualiza o `Produto.quantidade` no banco.

Implementação:
- UI/alerta e ação: [estoque/ui.py](file:///c:/Projetos/baleia/app/modules/estoque/ui.py)
- Persistência: [estoque/service.py](file:///c:/Projetos/baleia/app/modules/estoque/service.py#L49-L68)

### 5.4 Relatório de estoque
1. Clique **Imprimir Relatório**.
2. Escolha impressora / “Microsoft Print to PDF”.
3. Confirme.

O relatório inclui cabeçalho institucional com logo.

## 6. Clientes / Fiado

### 6.1 Cadastrar cliente
1. Vá em **Clientes / Fiado**.
2. Clique **+ Novo Cliente**.
3. Preencha nome e dados (telefone/e-mail opcionais).

### 6.2 Ver histórico detalhado
1. Selecione o cliente.
2. Clique **Ver** (na linha).

Você verá:
- Débitos (compras fiadas)
- Créditos (pagamentos)

### 6.3 Receber pagamento de dívida
1. Clique **Pagar** (na linha) ou selecione e clique **Receber Pagamento**.
2. Informe valor e observação.

Resultado esperado:
- Cria registro `Fiado.tipo='CREDITO'`
- Reduz `Cliente.divida_atual`
- Registra **ENTRADA** no fluxo de caixa com “Pagamento de dívida: Nome”

Regras: [fiado/service.py](file:///c:/Projetos/baleia/app/modules/fiado/service.py#L70-L107)

### 6.4 Imprimir relatório de clientes e débitos
1. Clique **Imprimir Lista**.
2. Se houver seleção, escolha imprimir “selecionados” ou “todos”.
3. Confirme no diálogo de impressão.

## 7. Fluxo de Caixa

### 7.1 Visão geral
O módulo mostra:
- Saldo em caixa (calculado por entradas - saídas)
- Entradas do mês, saídas do mês e balanço

### 7.2 Registrar entrada extra
1. Clique **+ Registrar Entrada Extra**.
2. Informe valor e descrição.

### 7.3 Registrar despesa/retirada (SAÍDA)
1. Clique **- Registrar Despesa / Retirada**.
2. Selecione uma categoria (Tipos de Despesa).
3. Informe valor e observação.

Persistência e regras:
- Saldo atual considera entradas e saídas conforme tipos: [fluxo_caixa/service.py](file:///c:/Projetos/baleia/app/modules/fluxo_caixa/service.py#L12-L29)
- Registrar saída: [fluxo_caixa/service.py](file:///c:/Projetos/baleia/app/modules/fluxo_caixa/service.py#L31-L48)

### 7.4 Filtrar e imprimir relatório do período
1. Ajuste “De” e “Até”.
2. Clique **Filtrar** (atualiza a tabela).
3. Clique **Imprimir Relatório**.

O relatório inclui cabeçalho institucional com logo.

## 8. Tipos de Despesa (Categorias)

### 8.1 Criar categoria
1. Vá em **Tipos de Despesas**.
2. Clique **+ Novo Tipo**.
3. Preencha nome e descrição (opcional).
4. Marque “Categoria Ativa” se aplicável.

### 8.2 Excluir categoria (com preservação de histórico)
Regras:
- Se existir movimentação vinculada, o sistema **inativa** ao invés de excluir.
- Caso não exista vínculo, exclui definitivamente.

Serviço: [tipos_despesa/service.py](file:///c:/Projetos/baleia/app/modules/configuracoes/tipos_despesa/service.py#L98-L118)

## 9. Configurações

Em **Configurações**, você define:
- Dados institucionais (empresa)
- Pasta de relatórios
- Estoque mínimo global
- Logo (caminho do arquivo)
- BRNews URL (para o dashboard)
- Rodapé do ticket
- Observação dos relatórios

Arquivo de configuração:
- `config/settings.json`

Padrões e chaves: [config.py](file:///c:/Projetos/baleia/app/core/config.py)

## 10. Impressão e PDF (Dicas)

- Para gerar PDF, utilize “Microsoft Print to PDF” ou driver equivalente.
- Caso o logo não apareça na impressão, verifique:
  - `empresa_logo_path` em Configurações
  - arquivo existente no caminho informado
- O sistema utiliza URI absoluta (`file:///...`) no HTML para garantir compatibilidade.

## 11. Solução de Problemas

### 11.1 Notícias com falha
Possíveis causas:
- BRNews fora do ar / URL incorreta
- Bloqueio de rede/firewall

Ação:
- Ajuste `BRNews URL` nas Configurações.
- O sistema tenta fallback via RSS.

### 11.2 Estoque não baixa após venda
Verifique:
- Venda foi efetivamente “recebida” (persistida)
- Produto tinha quantidade suficiente (o sistema bloqueia venda se estoque insuficiente)

### 11.3 Impressão sem logo
Verifique:
- Configuração `empresa_logo_path`
- Existência do arquivo no ambiente (dev e `.exe`)
