import '../../core/constants/app_constants.dart';
import '../../core/utils/local_cache.dart';
import '../../core/utils/outbox_store.dart';
import '../../data/datasources/supabase_datasource.dart';
import '../../data/dtos/fluxo_lancamento_dto.dart';
import '../../data/models/fluxo_item.dart';
import '../../data/repositories/repository_exception.dart';

class FluxoRepository {
  final SupabaseDatasource _datasource;

  FluxoRepository(this._datasource);

  /// Lista movimento de caixa com fallback offline.
  Future<List<FluxoItem>> getFluxo({DateTime? inicio, DateTime? fim}) async {
    try {
      final data = await _datasource.fetchFluxo(inicio: inicio, fim: fim);
      await LocalCache.write(AppConstants.cacheFluxo, {'items': data});
      return data.map(FluxoItem.fromJson).toList();
    } catch (e) {
      final cache = await LocalCache.read(AppConstants.cacheFluxo);
      final raw = cache?['items'];
      if (raw is List) {
        return raw.map((item) => FluxoItem.fromJson(Map<String, dynamic>.from(item as Map))).toList();
      }
      throw RepositoryException('Falha ao carregar fluxo: $e');
    }
  }

  /// Registra um lançamento administrativo no fluxo.
  Future<bool> registrarLancamento(FluxoLancamentoDto dto) async {
    try {
      await _datasource.registrarLancamentoFluxo(dto);
      return false;
    } catch (_) {
      await OutboxStore.enqueue(
        type: 'fluxo_lancamento',
        payload: dto.toJson(),
      );
      return true;
    }
  }
}
