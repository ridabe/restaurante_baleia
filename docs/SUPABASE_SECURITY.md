# Supabase em produção — recomendação de segurança

Este projeto hoje consegue conectar ao Postgres do Supabase via `DATABASE_URL` (SQLAlchemy). Isso funciona, mas existem riscos importantes em produção, especialmente quando o sistema é distribuído como `.exe`.

## 1) Não embutir senha do Postgres no executável

Se o `.exe` contém `DATABASE_URL` com usuário/senha do Postgres:
- qualquer pessoa com acesso ao arquivo pode extrair credenciais
- o acesso é direto ao banco (alto impacto em caso de vazamento)

Recomendação mínima:
- usar `.env` no computador do cliente (não versionado)
- restringir permissões do usuário do banco (se possível)

## 2) Modelo recomendado (mais seguro)

Para produção em escala, prefira:
- Supabase Auth + RLS e acesso via API do Supabase (anon key)
ou
- um backend intermediário (API) que usa `service_role` e expõe apenas operações necessárias

Isso permite:
- revogar acesso por usuário
- auditar operações
- aplicar políticas (RLS) de forma consistente

## 3) RLS

Se o objetivo for acessar tabelas via API do Supabase:
- habilite RLS em tabelas do schema exposto (geralmente `public`)
- crie policies compatíveis com o modelo de acesso do produto

## 4) Próximos passos sugeridos para este projeto

- definir o modelo de autenticação (login e permissões)
- definir o modelo de acesso (API vs conexão direta)
- criar policies RLS e funções seguras (quando necessário)
