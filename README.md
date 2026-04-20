# 🍻 Bar do Baleia — Sistema de Gestão

Sistema desktop moderno para gestão operacional de bares e restaurantes, desenvolvido com Python e PySide6.

## 🎯 Funcionalidades

- **💰 Módulo de Caixa (PDV):** Registro de vendas rápidas com suporte a Dinheiro, Cartão, Pix e Fiado.
- **📦 Módulo de Estoque:** Cadastro e controle de produtos com alertas de estoque baixo.
- **📒 Módulo de Fiado:** Gestão de clientes e controle de dívidas com histórico de pagamentos.
- **📊 Fluxo de Caixa:** Monitoramento automático de entradas e saídas com resumo mensal e diário.
- **⚙️ Configurações:** Personalização do nome da empresa e preferências do sistema.
- **✝️ Versículo do Dia:** Exibição automática de versículos bíblicos (Bible API).

## 🧱 Requisitos Técnicos

- Python 3.11+
- PySide6 (Interface Gráfica)
- SQLAlchemy (ORM)
- SQLite (Banco de dados local)

## 📁 Estrutura do Projeto

```text
/app
  /core         # Banco de dados, modelos e configurações
  /modules      # Lógica e UI de cada módulo (Caixa, Estoque, etc)
  /services     # Serviços externos (Bible API)
  /ui           # Janela principal e componentes comuns
/config         # Arquivos de configuração (settings.json)
/logs           # Logs do sistema
/relatorios     # Exportação de relatórios (PDF)
main.py         # Ponto de entrada da aplicação
```

## 🚀 Como Executar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Execute o sistema:
   ```bash
   python main.py
   ```

## 📦 Como Gerar o Executável (.exe)

Para gerar o executável para Windows:

```bash
pyinstaller --noconsole --onefile --name "BarDoBaleia" --add-data "app;app" main.py
```

Opcional (ícone):
- Converta um PNG para `.ico` (ex.: `app/img/logo_baleia.png` → `icon.ico`) e então use:

```bash
pyinstaller --noconsole --onefile --name "BarDoBaleia" --add-data "app;app" --icon=icon.ico main.py
```

Se existir um `BarDoBaleia.spec` antigo apontando para `icon.ico`, apague o `.spec` e rode novamente.
*(Nota: Certifique-se de que as pastas `config`, `logs`, `relatorios` e o arquivo `database.db` serão criados automaticamente na primeira execução no mesmo diretório do .exe)*

## 🧠 Boas Práticas

- Arquitetura modular e desacoplada.
- Tratamento de exceções e logging rigoroso.
- Persistência local segura com SQLite.
