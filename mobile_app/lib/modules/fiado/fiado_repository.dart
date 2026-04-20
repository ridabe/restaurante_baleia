import '../../core/constants/app_constants.dart';
import '../../core/utils/local_cache.dart';
import '../../core/utils/outbox_store.dart';
import '../../data/datasources/supabase_datasource.dart';
import '../../data/dtos/pagamento_fiado_dto.dart';
import '../../data/models/cliente.dart';
import '../../data/models/fiado_lancamento.dart';
import '../../data/repositories/repository_exception.dart';

class FiadoRepository {
  final SupabaseDatasource _datasource;

  FiadoRepository(this._datasource);

  /// Retorna clientes do fiado com fallback offline.
  Future<List<Cliente>> getClientes({String? search}) async {
    try {
      final data = await _datasource.fetchClientes(search: search);
      await LocalCache.write(AppConstants.cacheClientes, {'items': data});
      return data.map(Cliente.fromJson).toList();
    } catch (e) {
      final cache = await LocalCache.read(AppConstants.cacheClientes);
      final raw = cache?['items'];
      if (raw is List) {
        return raw.map((item) => Cliente.fromJson(Map<String, dynamic>.from(item as Map))).toList();
      }
      throw RepositoryException('Falha ao carregar clientes: $e');
    }
  }

  /// Retorna histórico de lançamentos de fiado de um cliente.
  Future<List<FiadoLancamento>> getHistorico(int clienteId) async {
    final data = await _datasource.fetchHistoricoFiado(clienteId);
    return data.map(FiadoLancamento.fromJson).toList();
  }

  /// Aplica pagamento de fiado e gera entrada automática no fluxo.
  Future<bool> registrarPagamento(PagamentoFiadoDto dto) async {
    try {
      await _datasource.registrarPagamentoFiado(dto);
      return false;
    } catch (_) {
      await OutboxStore.enqueue(
        type: 'fiado_pagamento',
        payload: {
          'cliente_id': dto.clienteId,
          'valor': dto.valor,
          'descricao': dto.descricao,
          'meio_pagamento': dto.meioPagamento,
        },
      );
      return true;
    }
  }
}
