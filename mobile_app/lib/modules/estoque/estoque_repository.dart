import '../../core/constants/app_constants.dart';
import '../../core/utils/local_cache.dart';
import '../../core/utils/outbox_store.dart';
import '../../data/datasources/supabase_datasource.dart';
import '../../data/models/produto.dart';
import '../../data/repositories/repository_exception.dart';

class EstoqueRepository {
  final SupabaseDatasource _datasource;

  EstoqueRepository(this._datasource);

  /// Busca produtos no Supabase com fallback no cache local.
  Future<List<Produto>> getProdutos({String? search}) async {
    try {
      final data = await _datasource.fetchProdutos(search: search);
      await LocalCache.write(AppConstants.cacheProdutos, {'items': data});
      return data.map(Produto.fromJson).toList();
    } catch (e) {
      final cache = await LocalCache.read(AppConstants.cacheProdutos);
      final raw = cache?['items'];
      if (raw is List) {
        return raw.map((item) => Produto.fromJson(Map<String, dynamic>.from(item as Map))).toList();
      }
      throw RepositoryException('Falha ao carregar estoque: $e');
    }
  }

  /// Atualiza estoque de um produto diretamente no Supabase.
  Future<bool> atualizarQuantidade(int produtoId, int quantidade) async {
    try {
      await _datasource.updateProdutoQuantidade(produtoId: produtoId, quantidade: quantidade);
      return false;
    } catch (_) {
      await OutboxStore.enqueue(
        type: 'estoque_update',
        payload: {
          'produto_id': produtoId,
          'quantidade': quantidade,
        },
      );
      return true;
    }
  }
}
