import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/datasources/supabase_datasource.dart';
import '../../data/models/dashboard_resumo.dart';
import '../../data/models/dashboard_serie.dart';
import '../../data/models/estoque_alerta.dart';
import '../../data/models/fiado_cliente_resumo.dart';
import '../../data/models/movimento_recente.dart';
import '../../data/models/top_produto.dart';
import 'dashboard_repository.dart';

class DashboardState {
  final DashboardResumo? resumo;
  final List<DashboardSerie> serie;
  final List<Map<String, dynamic>> despesasCategoria;
  final List<TopProduto> topProdutosDia;
  final List<EstoqueAlerta> alertasEstoqueBaixo;
  final List<FiadoClienteResumo> gestaoFiado;
  final List<MovimentoRecente> ultimasMovimentacoes;

  const DashboardState({
    required this.resumo,
    required this.serie,
    required this.despesasCategoria,
    required this.topProdutosDia,
    required this.alertasEstoqueBaixo,
    required this.gestaoFiado,
    required this.ultimasMovimentacoes,
  });

  DashboardState copyWith({
    DashboardResumo? resumo,
    List<DashboardSerie>? serie,
    List<Map<String, dynamic>>? despesasCategoria,
    List<TopProduto>? topProdutosDia,
    List<EstoqueAlerta>? alertasEstoqueBaixo,
    List<FiadoClienteResumo>? gestaoFiado,
    List<MovimentoRecente>? ultimasMovimentacoes,
  }) {
    return DashboardState(
      resumo: resumo ?? this.resumo,
      serie: serie ?? this.serie,
      despesasCategoria: despesasCategoria ?? this.despesasCategoria,
      topProdutosDia: topProdutosDia ?? this.topProdutosDia,
      alertasEstoqueBaixo: alertasEstoqueBaixo ?? this.alertasEstoqueBaixo,
      gestaoFiado: gestaoFiado ?? this.gestaoFiado,
      ultimasMovimentacoes: ultimasMovimentacoes ?? this.ultimasMovimentacoes,
    );
  }
}

final dashboardDatasourceProvider = Provider((ref) => SupabaseDatasource());
final dashboardRepositoryProvider = Provider((ref) => DashboardRepository(ref.read(dashboardDatasourceProvider)));

final dashboardControllerProvider = StateNotifierProvider<DashboardController, AsyncValue<DashboardState>>(
  (ref) => DashboardController(ref.read(dashboardRepositoryProvider))..load(),
);

class DashboardController extends StateNotifier<AsyncValue<DashboardState>> {
  final DashboardRepository _repository;

  DashboardController(this._repository) : super(const AsyncLoading());

  /// Carrega cards e gráficos do dashboard.
  Future<void> load() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final resumo = await _repository.getResumo();
      final serie = await _repository.getSerie7Dias();
      final despesas = await _repository.getDespesasCategoria();
      final topProdutos = await _repository.getTopProdutosDia(limit: 10);
      final alertasEstoque = await _repository.getAlertasEstoqueBaixo(limit: 10);
      final gestaoFiado = await _repository.getGestaoFiado(limit: 6);
      final movimentacoes = await _repository.getUltimasMovimentacoes(limit: 10);
      return DashboardState(
        resumo: resumo,
        serie: serie,
        despesasCategoria: despesas,
        topProdutosDia: topProdutos,
        alertasEstoqueBaixo: alertasEstoque,
        gestaoFiado: gestaoFiado,
        ultimasMovimentacoes: movimentacoes,
      );
    });
  }
}
