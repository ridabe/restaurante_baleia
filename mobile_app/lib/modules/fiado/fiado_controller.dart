import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/datasources/supabase_datasource.dart';
import '../../data/dtos/pagamento_fiado_dto.dart';
import '../../data/models/cliente.dart';
import '../../data/models/fiado_lancamento.dart';
import 'fiado_repository.dart';

final fiadoDatasourceProvider = Provider((ref) => SupabaseDatasource());
final fiadoRepositoryProvider = Provider((ref) => FiadoRepository(ref.read(fiadoDatasourceProvider)));

final fiadoControllerProvider = StateNotifierProvider<FiadoController, AsyncValue<List<Cliente>>>(
  (ref) => FiadoController(ref.read(fiadoRepositoryProvider))..load(),
);

class FiadoController extends StateNotifier<AsyncValue<List<Cliente>>> {
  final FiadoRepository _repository;

  FiadoController(this._repository) : super(const AsyncLoading());

  /// Carrega listagem de clientes do módulo fiado.
  Future<void> load({String? search}) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => _repository.getClientes(search: search));
  }

  /// Busca histórico de fiado para detalhamento do cliente.
  Future<List<FiadoLancamento>> getHistorico(int clienteId) {
    return _repository.getHistorico(clienteId);
  }

  /// Registra pagamento de fiado e atualiza a listagem.
  Future<bool> pagarFiado({required int clienteId, required double valor, required String descricao}) async {
    final queued = await _repository.registrarPagamento(
      PagamentoFiadoDto(clienteId: clienteId, valor: valor, descricao: descricao, meioPagamento: 'DINHEIRO'),
    );
    await load();
    return queued;
  }
}
