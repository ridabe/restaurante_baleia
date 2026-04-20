import '../../core/constants/app_constants.dart';
import '../../core/utils/local_cache.dart';
import '../../data/datasources/supabase_datasource.dart';
import '../../data/models/dashboard_resumo.dart';
import '../../data/models/dashboard_serie.dart';
import '../../data/models/estoque_alerta.dart';
import '../../data/models/fiado_cliente_resumo.dart';
import '../../data/models/movimento_recente.dart';
import '../../data/models/top_produto.dart';
import '../../data/repositories/repository_exception.dart';

class DashboardRepository {
  final SupabaseDatasource _datasource;

  DashboardRepository(this._datasource);

  /// Retorna resumo do dashboard com fallback offline em caso de erro.
  Future<DashboardResumo> getResumo() async {
    try {
      final json = await _datasource.fetchDashboardResumo();
      await LocalCache.write(AppConstants.cacheDashboard, {
        'resumo': json,
      });
      return DashboardResumo.fromJson(json);
    } catch (e) {
      final cached = await LocalCache.read(AppConstants.cacheDashboard);
      if (cached != null && cached['resumo'] is Map<String, dynamic>) {
        return DashboardResumo.fromJson(cached['resumo'] as Map<String, dynamic>);
      }
      throw RepositoryException('Falha ao carregar resumo do dashboard: $e');
    }
  }

  /// Retorna série de 7 dias para gráfico de entradas x saídas.
  Future<List<DashboardSerie>> getSerie7Dias() async {
    final data = await _datasource.fetchSerieFluxo7Dias();
    return data.map(DashboardSerie.fromJson).toList();
  }

  /// Retorna despesas por categoria para gráfico de pizza.
  Future<List<Map<String, dynamic>>> getDespesasCategoria() {
    return _datasource.fetchDespesasPorCategoria();
  }

  /// Retorna lista de produtos mais vendidos do dia.
  Future<List<TopProduto>> getTopProdutosDia({int limit = 10}) async {
    final data = await _datasource.fetchProdutosMaisVendidosDia(limit: limit);
    return data
        .map(
          (e) => TopProduto(
            produtoId: e['produto_id'] as int,
            nome: e['nome'] as String? ?? '',
            quantidade: e['quantidade'] as int? ?? 0,
            totalVendido: (e['total'] as num?)?.toDouble() ?? 0,
          ),
        )
        .toList();
  }

  /// Retorna alertas de estoque baixo com quantidade atual e mínimo.
  Future<List<EstoqueAlerta>> getAlertasEstoqueBaixo({int limit = 10}) async {
    final data = await _datasource.fetchAlertasEstoqueBaixo(limit: limit);
    return data
        .map(
          (e) => EstoqueAlerta(
            produtoId: e['id'] as int,
            nome: e['nome'] as String? ?? '',
            atual: e['quantidade'] as int? ?? 0,
            minimo: e['estoque_minimo'] as int? ?? 0,
          ),
        )
        .toList();
  }

  /// Retorna gestão de fiado (maiores devedores).
  Future<List<FiadoClienteResumo>> getGestaoFiado({int limit = 6}) async {
    final data = await _datasource.fetchGestaoFiado(limit: limit);
    return data
        .map(
          (e) => FiadoClienteResumo(
            id: e['id'] as int,
            nome: e['nome'] as String? ?? '',
            telefone: e['telefone'] as String?,
            divida: (e['divida_atual'] as num?)?.toDouble() ?? 0,
          ),
        )
        .toList();
  }

  /// Retorna últimas movimentações do fluxo.
  Future<List<MovimentoRecente>> getUltimasMovimentacoes({int limit = 10}) async {
    final data = await _datasource.fetchUltimasMovimentacoes(limit: limit);
    return data
        .map(
          (e) => MovimentoRecente(
            id: e['id'] as int,
            tipo: e['tipo'] as String? ?? '',
            valor: (e['valor'] as num?)?.toDouble() ?? 0,
            descricao: e['descricao'] as String? ?? '',
            dataRegistro: DateTime.parse(e['data_registro'] as String),
          ),
        )
        .toList();
  }
}
