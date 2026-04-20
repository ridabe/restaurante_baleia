# Migração futura — SQLite (local) → Supabase (PostgreSQL)

Este documento descreve como o projeto está preparado para migrar do banco local (SQLite) para um banco remoto (Supabase/PostgreSQL) e quais passos serão necessários quando a migração for iniciada.

## 1. Como o sistema decide qual banco usar

O sistema resolve a URL do banco nesta ordem:
1. Variável de ambiente `DATABASE_URL`
2. Configuração `database_url` em `config/settings.json`
3. Fallback: SQLite local (`database.db`) na pasta do executável/projeto

Implementação: [database.py](file:///c:/Projetos/baleia/app/core/database.py#L16-L64)

## 2. O que você vai precisar no dia da migração

### 2.1 Supabase (PostgreSQL)
- Criar projeto no Supabase e obter a connection string do Postgres.
- Preferência: usar connection string no formato SQLAlchemy.

Importante:
- `SUPABASE_URL` e `SUPABASE_KEY` (anon/publishable) **não** são usados para criar tabelas via SQLAlchemy.
- Para criar tabelas e operar como banco relacional, é necessário o `DATABASE_URL` do Postgres.

Exemplos (variam por driver):
- `postgresql+psycopg2://USER:PASSWORD@HOST:5432/DATABASE`
- `postgresql://USER:PASSWORD@HOST:5432/DATABASE`

### 2.2 Dependência do driver Postgres
- Em desenvolvimento: instalar driver (ex.: `psycopg2-binary`).
- No executável PyInstaller: o driver precisa estar instalado no ambiente de build para ser empacotado.

## 3. Como testar localmente com Postgres (quando chegar a hora)

1. Configure `DATABASE_URL` no ambiente:
   - PowerShell:
     - `$env:DATABASE_URL="postgresql+psycopg2://..."`
2. Rode o sistema normalmente (`python main.py`)
3. O sistema criará tabelas via `Base.metadata.create_all()` se estiver vazio.

Observação:
- Migrações “leves” via `ALTER TABLE` só rodam em SQLite.
- Para Postgres, quando houver evolução de schema, o recomendado é introduzir Alembic.

## 3.1 Migrações em produção (Alembic)

Este repositório já inclui Alembic com:
- baseline (`0001_baseline`) vazio (para alinhar o histórico)
- índices (`0002_indexes`) com `IF NOT EXISTS`

Com `DATABASE_URL` apontando para o Supabase:

```bash
alembic -c alembic.ini upgrade head
```

## 4. Estratégia recomendada de migração de dados

Quando iniciar a migração, usar uma estratégia em 2 etapas:
1. Subir o schema no Supabase
2. Exportar dados do SQLite e importar no Postgres

Ferramentas típicas:
- export via SQLAlchemy (script de migração) ou dump do SQLite.

Script pronto no projeto:
- `python scripts/migrate_sqlite_to_supabase.py`

## 5. Preparação já realizada no código

- Engine inicializa de forma lazy e é configurado via URL:
  - Permite trocar de SQLite para Postgres sem refatorar services.
- `db_session` mantém a mesma interface.
- A criação das tabelas continua centralizada.

## 6. Backlog para “pronto para produção em Supabase”

- Adicionar Alembic (migrações reais em Postgres)
- Ajustar índices para consultas agregadas do dashboard (performance)
- Estratégia de credenciais e SSL (Supabase)
- Regras de concorrência / multiusuário (se necessário)
