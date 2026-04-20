# Bar do Baleia Mobile

Aplicativo Flutter para gestão mobile administrativa integrado ao Supabase.

## Segurança (Supabase)

No Supabase, aplique o script de segurança/RLS e funções RPC:

- `docs/SUPABASE_MOBILE_SECURITY.sql`

Recomendado:
- habilitar Supabase Auth (e-mail/senha)
- manter as tabelas bloqueadas para `anon` (o app usa `SUPABASE_ANON_KEY`, mas acessa dados como usuário autenticado)

## Configuração

1. Copie `.env.example` para `.env`.
2. Preencha `SUPABASE_URL` e `SUPABASE_ANON_KEY`.
3. Para teste rápido sem login, mantenha `REQUIRE_AUTH=false`.
4. Para exigir login, use `REQUIRE_AUTH=true`.
5. Rode:

```bash
flutter pub get
flutter run -d windows
```

## Build APK

```bash
flutter build apk
```

## Offline (modo híbrido)

- Leitura: fallback para cache local quando não houver conexão.
- Escrita: operações são enfileiradas no dispositivo (outbox) e sincronizadas via botão de sincronização no topo do app.
