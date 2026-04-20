import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/utils/currency_formatter.dart';
import '../../shared/widgets/error_widget_custom.dart';
import '../../shared/widgets/loading_widget.dart';
import 'fluxo_controller.dart';

class FluxoPage extends ConsumerWidget {
  const FluxoPage({super.key});

  /// Exibe diálogo de lançamento de entrada/saída para operação administrativa.
  Future<void> _openLancamentoDialog(BuildContext context, WidgetRef ref, String tipo) async {
    final valorController = TextEditingController();
    final descricaoController = TextEditingController();

    await showDialog<void>(
      context: context,
      builder: (_) => AlertDialog(
        title: Text(tipo == 'entrada' ? 'Nova entrada' : 'Nova saída'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: valorController,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(labelText: 'Valor'),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: descricaoController,
              decoration: const InputDecoration(labelText: 'Descrição'),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancelar')),
          ElevatedButton(
            onPressed: () async {
              final valor = double.tryParse(valorController.text.replaceAll(',', '.'));
              if (valor == null || valor <= 0) return;
              bool queued;
              if (tipo == 'entrada') {
                queued = await ref.read(fluxoControllerProvider.notifier).registrarEntrada(
                      valor: valor,
                      descricao: descricaoController.text,
                    );
              } else {
                queued = await ref.read(fluxoControllerProvider.notifier).registrarSaida(
                      valor: valor,
                      descricao: descricaoController.text,
                    );
              }
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(queued ? 'Sem conexão. Lançamento pendente para sincronização.' : 'Lançamento registrado.')),
                );
              }
              if (context.mounted) Navigator.pop(context);
            },
            child: const Text('Salvar'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(fluxoControllerProvider);
    return Scaffold(
      floatingActionButton: Column(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          FloatingActionButton.extended(
            onPressed: () => _openLancamentoDialog(context, ref, 'entrada'),
            heroTag: 'entrada',
            icon: const Icon(Icons.add),
            label: const Text('Entrada'),
          ),
          const SizedBox(height: 8),
          FloatingActionButton.extended(
            onPressed: () => _openLancamentoDialog(context, ref, 'saida'),
            heroTag: 'saida',
            icon: const Icon(Icons.remove),
            label: const Text('Saída'),
          ),
        ],
      ),
      body: state.when(
        loading: () => const LoadingWidget(message: 'Carregando fluxo...'),
        error: (error, _) => ErrorWidgetCustom(
          message: 'Erro no fluxo: $error',
          onRetry: () => ref.read(fluxoControllerProvider.notifier).load(),
        ),
        data: (itens) {
          final saldo = itens.fold<double>(
            0,
            (acc, item) => item.tipo == 'entrada' ? acc + item.valor : acc - item.valor,
          );
          return Column(
            children: [
              Card(
                margin: const EdgeInsets.all(16),
                child: ListTile(
                  title: const Text('Saldo Atual'),
                  subtitle: Text(CurrencyFormatter.brl(saldo)),
                ),
              ),
              Expanded(
                child: ListView.builder(
                  itemCount: itens.length,
                  itemBuilder: (context, index) {
                    final item = itens[index];
                    return Card(
                      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                      child: ListTile(
                        title: Text(item.descricao ?? '-'),
                        subtitle: Text(item.dataRegistro.toString()),
                        trailing: Text(
                          CurrencyFormatter.brl(item.valor),
                          style: TextStyle(color: item.tipo == 'entrada' ? Colors.green : Colors.red),
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
