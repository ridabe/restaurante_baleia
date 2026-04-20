# Supabase (PostgreSQL) — Setup do Banco para o Bar do Baleia

Este projeto hoje roda com SQLite local. Para migrar para Supabase/PostgreSQL, você precisa **da connection string do Postgres** (não é o mesmo que `SUPABASE_URL`/`SUPABASE_KEY`).

## 1) Gerar o SQL das tabelas do sistema

1. No projeto, rode:

```bash
python scripts/generate_schema_postgres.py
```

2. O arquivo gerado será:
- `docs/supabase_schema.sql`

3. No Supabase:
- Acesse **SQL Editor**
- Cole o conteúdo do `supabase_schema.sql`
- Execute

Isso cria todas as tabelas com colunas conforme os models atuais.

## 2) Apontar o sistema para o Supabase

Você precisa obter no Supabase:
- **Host**, **Port**, **Database**, **User**, **Password**
- Ou a connection string pronta (Settings → Database → Connection string)

Depois, configure **uma** destas opções:

### Opção A (recomendada): variável de ambiente
- `DATABASE_URL` (formato SQLAlchemy)

Exemplo:
```powershell
$env:DATABASE_URL="postgresql+psycopg2://postgres:SUA_SENHA@db.vtoqconagqtezpceezvg.supabase.co:5432/postgres?sslmode=require"
python main.py
```

### Opção B: settings.json (para ambiente local)
- `config/settings.json` → `database_url`

Observações importantes:
- Use `?sslmode=require` (Supabase normalmente exige SSL).
- Se a senha tiver caracteres especiais, faça URL-encode (ex.: `@` vira `%40`).

## 2.1) Criar as tabelas automaticamente via SQLAlchemy (opcional)

Após configurar `DATABASE_URL`, rode:

```bash
python scripts/init_supabase_db.py
```

Isso executa `create_all()` e cria as tabelas no Postgres (Supabase) conforme os models atuais.

## 2.2) Migrações em produção (Alembic)

Para uso em produção, as mudanças de schema devem ser versionadas com Alembic.

1. Garanta `DATABASE_URL` apontando para o Supabase.
2. Rode:

```bash
alembic -c alembic.ini upgrade head
```

Se as tabelas foram criadas anteriormente via `create_all()`, o baseline do Alembic é um `upgrade()` vazio e o migration de índices usa `IF NOT EXISTS`, então é seguro.

## 2.3) Migrar dados do SQLite local para o Supabase

Com `DATABASE_URL` configurado no `.env`, rode:

```bash
python scripts/migrate_sqlite_to_supabase.py
```

Por padrão ele migra do arquivo local `database.db` na pasta do app.
Para apontar para outro arquivo SQLite, defina:

```bash
set SQLITE_PATH=C:\caminho\para\database.db
python scripts/migrate_sqlite_to_supabase.py
```

## 3) Importante sobre SUPABASE_URL e SUPABASE_KEY

- `SUPABASE_URL`/`SUPABASE_KEY` são usados para API do Supabase (REST/Auth/Storage).
- Para SQLAlchemy operar como banco relacional, você precisa do **Postgres DATABASE_URL**.

## 4) Driver Postgres

Para conectar em Postgres:
- em dev: instalar `psycopg2-binary`
- para build `.exe`: o driver precisa estar instalado no ambiente que executa `build.py` para ser empacotado.
