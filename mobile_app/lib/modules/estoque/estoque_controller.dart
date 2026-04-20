import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/datasources/supabase_datasource.dart';
import '../../data/models/produto.dart';
import 'estoque_repository.dart';

final estoqueDatasourceProvider = Provider((ref) => SupabaseDatasource());
final estoqueRepositoryProvider = Provider((ref) => EstoqueRepository(ref.read(estoqueDatasourceProvider)));

final estoqueControllerProvider = StateNotifierProvider<EstoqueController, AsyncValue<List<Produto>>>(
  (ref) => EstoqueController(ref.read(estoqueRepositoryProvider))..load(),
);

class EstoqueController extends StateNotifier<AsyncValue<List<Produto>>> {
  final EstoqueRepository _repository;

  EstoqueController(this._repository) : super(const AsyncLoading());

  /// Carrega listagem de produtos com filtro opcional.
  Future<void> load({String? search}) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => _repository.getProdutos(search: search));
  }

  /// Salva novo saldo de estoque e recarrega a lista.
  Future<bool> atualizarQuantidade(int produtoId, int quantidade) async {
    final queued = await _repository.atualizarQuantidade(produtoId, quantidade);
    await load();
    return queued;
  }
}
