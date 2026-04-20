import '../core/utils/outbox_store.dart';
import '../data/datasources/supabase_datasource.dart';
import '../data/dtos/fluxo_lancamento_dto.dart';
import '../data/dtos/pagamento_fiado_dto.dart';

class SyncService {
  final SupabaseDatasource _datasource;

  SyncService(this._datasource);

  Future<int> sync() async {
    final items = await OutboxStore.readAll();
    if (items.isEmpty) {
      return 0;
    }

    var synced = 0;
    final remaining = <Map<String, dynamic>>[];

    for (final item in items) {
      final type = item['type'] as String?;
      final payload = item['payload'];
      if (type == null || payload is! Map) {
        continue;
      }

      try {
        final data = Map<String, dynamic>.from(payload);
        if (type == 'estoque_update') {
          await _datasource.updateProdutoQuantidade(
            produtoId: data['produto_id'] as int,
            quantidade: data['quantidade'] as int,
          );
          synced += 1;
          continue;
        }

        if (type == 'fluxo_lancamento') {
          await _datasource.registrarLancamentoFluxo(
            FluxoLancamentoDto(
              tipo: data['tipo'] as String,
              valor: (data['valor'] as num).toDouble(),
              descricao: data['descricao'] as String,
              meioPagamento: data['meio_pagamento'] as String?,
              tipoDespesaId: data['tipo_despesa_id'] as int?,
            ),
          );
          synced += 1;
          continue;
        }

        if (type == 'fiado_pagamento') {
          await _datasource.registrarPagamentoFiado(
            PagamentoFiadoDto(
              clienteId: data['cliente_id'] as int,
              valor: (data['valor'] as num).toDouble(),
              descricao: data['descricao'] as String,
              meioPagamento: (data['meio_pagamento'] as String?) ?? 'DINHEIRO',
            ),
          );
          synced += 1;
          continue;
        }

        remaining.add(item);
      } catch (_) {
        remaining.add(item);
      }
    }

    await OutboxStore.replaceAll(remaining);
    return synced;
  }
}
