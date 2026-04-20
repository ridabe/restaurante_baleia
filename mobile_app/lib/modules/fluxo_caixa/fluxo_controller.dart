import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/datasources/supabase_datasource.dart';
import '../../data/dtos/fluxo_lancamento_dto.dart';
import '../../data/models/fluxo_item.dart';
import 'fluxo_repository.dart';

final fluxoDatasourceProvider = Provider((ref) => SupabaseDatasource());
final fluxoRepositoryProvider = Provider((ref) => FluxoRepository(ref.read(fluxoDatasourceProvider)));

final fluxoControllerProvider = StateNotifierProvider<FluxoController, AsyncValue<List<FluxoItem>>>(
  (ref) => FluxoController(ref.read(fluxoRepositoryProvider))..load(),
);

class FluxoController extends StateNotifier<AsyncValue<List<FluxoItem>>> {
  final FluxoRepository _repository;

  FluxoController(this._repository) : super(const AsyncLoading());

  /// Carrega fluxo de caixa aplicando filtro de período quando informado.
  Future<void> load({DateTime? inicio, DateTime? fim}) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => _repository.getFluxo(inicio: inicio, fim: fim));
  }

  /// Registra entrada manual no caixa e atualiza a listagem.
  Future<bool> registrarEntrada({required double valor, required String descricao}) async {
    final queued = await _repository.registrarLancamento(
      FluxoLancamentoDto(tipo: 'entrada', valor: valor, descricao: descricao, meioPagamento: 'indefinido'),
    );
    await load();
    return queued;
  }

  /// Registra saída manual no caixa e atualiza a listagem.
  Future<bool> registrarSaida({required double valor, required String descricao, int? tipoDespesaId}) async {
    final queued = await _repository.registrarLancamento(
      FluxoLancamentoDto(
        tipo: 'saida',
        valor: valor,
        descricao: descricao,
        meioPagamento: 'indefinido',
        tipoDespesaId: tipoDespesaId,
      ),
    );
    await load();
    return queued;
  }
}
