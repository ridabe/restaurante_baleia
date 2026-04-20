import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../core/utils/currency_formatter.dart';
import '../../data/models/dashboard_serie.dart';
import '../../data/models/estoque_alerta.dart';
import '../../data/models/fiado_cliente_resumo.dart';
import '../../data/models/movimento_recente.dart';
import '../../data/models/top_produto.dart';
import '../../shared/widgets/card_resumo.dart';
import '../../shared/widgets/empty_state.dart';
import '../../shared/widgets/error_widget_custom.dart';
import '../../shared/widgets/loading_widget.dart';
import 'dashboard_controller.dart';

class DashboardPage extends ConsumerWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(dashboardControllerProvider);
    return state.when(
      loading: () => const LoadingWidget(message: 'Carregando dashboard...'),
      error: (error, _) => ErrorWidgetCustom(
        message: 'Erro ao carregar dashboard: $error',
        onRetry: () => ref.read(dashboardControllerProvider.notifier).load(),
      ),
      data: (data) {
        final resumo = data.resumo;
        if (resumo == null) {
          return const EmptyState(message: 'Sem dados para o dashboard.');
        }
        return RefreshIndicator(
          onRefresh: () => ref.read(dashboardControllerProvider.notifier).load(),
          child: LayoutBuilder(
            builder: (context, constraints) {
              final width = constraints.maxWidth;
              final columns = width >= 1200 ? 6 : (width >= 800 ? 3 : 2);
              return ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  GridView.count(
                    crossAxisCount: columns,
                    crossAxisSpacing: 12,
                    mainAxisSpacing: 12,
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    children: [
                      CardResumo(titulo: 'Entradas', valor: CurrencyFormatter.brl(resumo.entradasDia), color: Colors.green),
                      CardResumo(titulo: 'Saídas', valor: CurrencyFormatter.brl(resumo.saidasDia), color: Colors.red),
                      CardResumo(titulo: 'Saldo', valor: CurrencyFormatter.brl(resumo.saldoDia), color: Colors.blue),
                      CardResumo(titulo: 'Fiado', valor: CurrencyFormatter.brl(resumo.totalFiado), color: Colors.orange),
                      CardResumo(titulo: 'Devedores', valor: resumo.clientesDevedores.toString(), color: Colors.deepPurple),
                      CardResumo(titulo: 'Estoque Baixo', valor: resumo.estoqueBaixo.toString(), color: Colors.brown),
                    ],
                  ),
                  const SizedBox(height: 16),
                  _ChartCard(serie: data.serie),
                  const SizedBox(height: 16),
                  _CategoriaCard(data: data.despesasCategoria),
                  const SizedBox(height: 16),
                  _TopProdutosCard(items: data.topProdutosDia),
                  const SizedBox(height: 16),
                  _FiadoCard(items: data.gestaoFiado, total: resumo.totalFiado),
                  const SizedBox(height: 16),
                  _EstoqueBaixoCard(items: data.alertasEstoqueBaixo),
                  const SizedBox(height: 16),
                  _UltimasMovimentacoesCard(items: data.ultimasMovimentacoes),
                ],
              );
            },
          ),
        );
      },
    );
  }
}

class _ChartCard extends StatelessWidget {
  final List<DashboardSerie> serie;

  const _ChartCard({required this.serie});

  @override
  Widget build(BuildContext context) {
    if (serie.isEmpty) {
      return const EmptyState(message: 'Sem dados de entradas x saídas.');
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Entradas x Saídas (7 dias)', style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 10),
            SizedBox(
              height: 220,
              child: LineChart(
                LineChartData(
                  gridData: const FlGridData(show: true),
                  borderData: FlBorderData(show: false),
                  titlesData: FlTitlesData(
                    topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    leftTitles: const AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 42)),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 28,
                        interval: 1,
                        getTitlesWidget: (value, meta) {
                          final idx = value.toInt();
                          if (idx < 0 || idx >= serie.length) return const SizedBox.shrink();
                          final d = serie[idx].dia;
                          return Padding(
                            padding: const EdgeInsets.only(top: 6),
                            child: Text('${d.day}/${d.month}', style: const TextStyle(fontSize: 10)),
                          );
                        },
                      ),
                    ),
                  ),
                  lineBarsData: [
                    LineChartBarData(
                      spots: List.generate(serie.length, (i) => FlSpot(i.toDouble(), serie[i].entradas)),
                      isCurved: true,
                      color: Colors.green,
                      barWidth: 3,
                      dotData: const FlDotData(show: false),
                    ),
                    LineChartBarData(
                      spots: List.generate(serie.length, (i) => FlSpot(i.toDouble(), serie[i].saidas)),
                      isCurved: true,
                      color: Colors.red,
                      barWidth: 3,
                      dotData: const FlDotData(show: false),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 10),
            const Wrap(
              spacing: 12,
              children: [
                _Legend(color: Colors.green, label: 'Entradas'),
                _Legend(color: Colors.red, label: 'Saídas'),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _Legend extends StatelessWidget {
  final Color color;
  final String label;

  const _Legend({required this.color, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(width: 10, height: 10, decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(2))),
        const SizedBox(width: 6),
        Text(label),
      ],
    );
  }
}

class _CategoriaCard extends StatelessWidget {
  final List<Map<String, dynamic>> data;

  const _CategoriaCard({required this.data});

  @override
  Widget build(BuildContext context) {
    if (data.isEmpty) {
      return const EmptyState(message: 'Sem despesas categorizadas.');
    }

    final max = data.fold<double>(0, (acc, e) {
      final value = (e['valor'] as num?)?.toDouble() ?? 0;
      return value > acc ? value : acc;
    });

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Despesas por categoria', style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 10),
            SizedBox(
              height: 260,
              child: BarChart(
                BarChartData(
                  maxY: max <= 0 ? 1 : max * 1.15,
                  gridData: const FlGridData(show: true),
                  borderData: FlBorderData(show: false),
                  titlesData: FlTitlesData(
                    topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    leftTitles: const AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 42)),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 42,
                        getTitlesWidget: (value, meta) {
                          final i = value.toInt();
                          if (i < 0 || i >= data.length) return const SizedBox.shrink();
                          final label = (data[i]['categoria']?.toString() ?? '-');
                          final short = label.length > 10 ? '${label.substring(0, 10)}…' : label;
                          return Padding(
                            padding: const EdgeInsets.only(top: 8),
                            child: Text(short, style: const TextStyle(fontSize: 10)),
                          );
                        },
                      ),
                    ),
                  ),
                  barGroups: List.generate(data.length, (i) {
                    final value = (data[i]['valor'] as num?)?.toDouble() ?? 0;
                    return BarChartGroupData(
                      x: i,
                      barRods: [
                        BarChartRodData(
                          toY: value,
                          color: Colors.orange,
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ],
                    );
                  }),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _TopProdutosCard extends StatelessWidget {
  final List<TopProduto> items;

  const _TopProdutosCard({required this.items});

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return const EmptyState(message: 'Sem produtos vendidos hoje.');
    }
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Produtos mais vendidos (hoje)', style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 10),
            ...items.take(10).map(
                  (p) => ListTile(
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    title: Text(p.nome),
                    subtitle: Text('Qtd: ${p.quantidade}'),
                    trailing: Text(CurrencyFormatter.brl(p.totalVendido)),
                  ),
                ),
          ],
        ),
      ),
    );
  }
}

class _FiadoCard extends StatelessWidget {
  final List<FiadoClienteResumo> items;
  final double total;

  const _FiadoCard({required this.items, required this.total});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Gestão de fiado', style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 6),
            Text('Total a receber: ${CurrencyFormatter.brl(total)}'),
            const SizedBox(height: 10),
            if (items.isEmpty)
              const Text('Sem clientes devedores no momento.')
            else
              ...items.map(
                (c) => ListTile(
                  dense: true,
                  contentPadding: EdgeInsets.zero,
                  title: Text(c.nome),
                  subtitle: Text(c.telefone ?? 'Sem telefone'),
                  trailing: Text(
                    CurrencyFormatter.brl(c.divida),
                    style: const TextStyle(color: Colors.red, fontWeight: FontWeight.w600),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _EstoqueBaixoCard extends StatelessWidget {
  final List<EstoqueAlerta> items;

  const _EstoqueBaixoCard({required this.items});

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return const EmptyState(message: 'Sem alertas de estoque baixo.');
    }
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Alertas de estoque baixo', style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 10),
            ...items.map(
              (p) => ListTile(
                dense: true,
                contentPadding: EdgeInsets.zero,
                title: Text(p.nome),
                subtitle: Text('Atual: ${p.atual} | Mínimo: ${p.minimo}'),
                trailing: const Icon(Icons.warning_amber, color: Colors.redAccent),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _UltimasMovimentacoesCard extends StatelessWidget {
  final List<MovimentoRecente> items;

  const _UltimasMovimentacoesCard({required this.items});

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      return const EmptyState(message: 'Sem movimentações recentes.');
    }
    final fmt = DateFormat('dd/MM HH:mm');
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Últimas movimentações', style: TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 10),
            ...items.map(
              (m) => ListTile(
                dense: true,
                contentPadding: EdgeInsets.zero,
                title: Text(m.descricao),
                subtitle: Text('${fmt.format(m.dataRegistro)} • ${m.tipo}'),
                trailing: Text(
                  CurrencyFormatter.brl(m.valor),
                  style: TextStyle(
                    color: m.tipo == 'entrada' ? Colors.green : Colors.red,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
