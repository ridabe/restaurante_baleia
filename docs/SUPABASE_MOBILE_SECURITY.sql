-- Bar do Baleia — Mobile (Supabase)
-- 1) RLS + policies (bloqueia anon e libera authenticated)
-- 2) Funções RPC para manter regras de negócio transacionais no banco

alter table public.produtos enable row level security;
alter table public.clientes enable row level security;
alter table public.fiados enable row level security;
alter table public.fluxo_caixa enable row level security;
alter table public.tipos_despesa enable row level security;
alter table public.vendas enable row level security;
alter table public.itens_venda enable row level security;

drop policy if exists "produtos_select_authenticated" on public.produtos;
create policy "produtos_select_authenticated"
on public.produtos
for select
to authenticated
using (true);

drop policy if exists "produtos_update_authenticated" on public.produtos;
create policy "produtos_update_authenticated"
on public.produtos
for update
to authenticated
using (true)
with check (true);

drop policy if exists "clientes_select_authenticated" on public.clientes;
create policy "clientes_select_authenticated"
on public.clientes
for select
to authenticated
using (true);

drop policy if exists "clientes_update_authenticated" on public.clientes;
create policy "clientes_update_authenticated"
on public.clientes
for update
to authenticated
using (true)
with check (true);

drop policy if exists "fiados_select_authenticated" on public.fiados;
create policy "fiados_select_authenticated"
on public.fiados
for select
to authenticated
using (true);

drop policy if exists "fiados_insert_authenticated" on public.fiados;
create policy "fiados_insert_authenticated"
on public.fiados
for insert
to authenticated
with check (true);

drop policy if exists "fluxo_select_authenticated" on public.fluxo_caixa;
create policy "fluxo_select_authenticated"
on public.fluxo_caixa
for select
to authenticated
using (true);

drop policy if exists "fluxo_insert_authenticated" on public.fluxo_caixa;
create policy "fluxo_insert_authenticated"
on public.fluxo_caixa
for insert
to authenticated
with check (true);

drop policy if exists "tipos_despesa_select_authenticated" on public.tipos_despesa;
create policy "tipos_despesa_select_authenticated"
on public.tipos_despesa
for select
to authenticated
using (true);

revoke all on public.produtos from anon;
revoke all on public.clientes from anon;
revoke all on public.fiados from anon;
revoke all on public.fluxo_caixa from anon;
revoke all on public.tipos_despesa from anon;
revoke all on public.vendas from anon;
revoke all on public.itens_venda from anon;

create or replace function public.registrar_pagamento_fiado(
  p_cliente_id integer,
  p_valor numeric,
  p_descricao text default 'Pagamento via mobile',
  p_meio_pagamento text default 'indefinido'
)
returns void
language plpgsql
as $$
declare
  v_divida_atual numeric;
  v_nova_divida numeric;
  v_cliente_nome text;
begin
  select divida_atual, nome
  into v_divida_atual, v_cliente_nome
  from public.clientes
  where id = p_cliente_id
  for update;

  v_divida_atual := coalesce(v_divida_atual, 0);
  v_nova_divida := greatest(v_divida_atual - p_valor, 0);

  insert into public.fiados (cliente_id, valor, tipo, descricao, data_registro)
  values (p_cliente_id, p_valor, 'credito', p_descricao, now());

  update public.clientes
  set divida_atual = v_nova_divida
  where id = p_cliente_id;

  insert into public.fluxo_caixa (tipo, meio_pagamento, valor, descricao, data_registro)
  values (
    'entrada',
    p_meio_pagamento,
    p_valor,
    'Pagamento de dívida | Cliente: ' || coalesce(v_cliente_nome, '') ||
    ' | Pago: R$ ' || to_char(p_valor, 'FM999999990.00') ||
    ' | Saldo restante: R$ ' || to_char(v_nova_divida, 'FM999999990.00') ||
    case when coalesce(p_meio_pagamento, '') <> '' then ' | Meio: ' || p_meio_pagamento else '' end ||
    case when coalesce(p_descricao, '') <> '' then ' | Obs: ' || p_descricao else '' end,
    now()
  );
end;
$$;

create or replace function public.registrar_lancamento_fluxo(
  p_tipo text,
  p_valor numeric,
  p_descricao text,
  p_meio_pagamento text default 'indefinido',
  p_tipo_despesa_id integer default null
)
returns void
language plpgsql
as $$
begin
  insert into public.fluxo_caixa (tipo, meio_pagamento, valor, descricao, data_registro, tipo_despesa_id)
  values (p_tipo, p_meio_pagamento, p_valor, p_descricao, now(), p_tipo_despesa_id);
end;
$$;

grant execute on function public.registrar_pagamento_fiado(integer, numeric, text, text) to authenticated;
grant execute on function public.registrar_lancamento_fluxo(text, numeric, text, text, integer) to authenticated;

