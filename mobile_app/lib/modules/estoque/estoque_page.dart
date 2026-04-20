import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/utils/currency_formatter.dart';
import '../../shared/widgets/campo_busca.dart';
import '../../shared/widgets/error_widget_custom.dart';
import '../../shared/widgets/loading_widget.dart';
import 'estoque_controller.dart';

class EstoquePage extends ConsumerStatefulWidget {
  const EstoquePage({super.key});

  @override
  ConsumerState<EstoquePage> createState() => _EstoquePageState();
}

class _EstoquePageState extends ConsumerState<EstoquePage> {
  final _searchController = TextEditingController();

  /// Dispara filtro de estoque por nome/código.
  void _search() {
    ref.read(estoqueControllerProvider.notifier).load(search: _searchController.text);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(estoqueControllerProvider);
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: CampoBusca(controller: _searchController, onSearch: _search, hint: 'Buscar por nome ou código'),
        ),
        Expanded(
          child: state.when(
            loading: () => const LoadingWidget(message: 'Carregando estoque...'),
            error: (error, _) => ErrorWidgetCustom(
              message: 'Erro no estoque: $error',
              onRetry: () => ref.read(estoqueControllerProvider.notifier).load(),
            ),
            data: (produtos) => ListView.builder(
              itemCount: produtos.length,
              itemBuilder: (context, index) {
                final item = produtos[index];
                return Card(
                  margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                  child: ListTile(
                    title: Text(item.nome),
                    subtitle: Text('${item.codigo} | ${CurrencyFormatter.brl(item.preco)}'),
                    trailing: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text('Qtd: ${item.quantidade}'),
                        Text(
                          'Min: ${item.estoqueMinimo}',
                          style: TextStyle(color: item.estoqueBaixo ? Colors.red : Colors.grey[700]),
                        ),
                      ],
                    ),
                    onTap: () => _openAdjustDialog(item.id, item.quantidade),
                  ),
                );
              },
            ),
          ),
        ),
      ],
    );
  }

  /// Abre modal para ajuste manual de quantidade no estoque.
  Future<void> _openAdjustDialog(int produtoId, int quantidadeAtual) async {
    final controller = TextEditingController(text: quantidadeAtual.toString());
    await showDialog<void>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Atualizar quantidade'),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.number,
          decoration: const InputDecoration(labelText: 'Nova quantidade'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancelar')),
          ElevatedButton(
            onPressed: () async {
              final nova = int.tryParse(controller.text);
              if (nova == null) return;
              final queued = await ref.read(estoqueControllerProvider.notifier).atualizarQuantidade(produtoId, nova);
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(queued ? 'Sem conexão. Ajuste pendente para sincronização.' : 'Quantidade atualizada.')),
                );
              }
              if (mounted) Navigator.pop(context);
            },
            child: const Text('Salvar'),
          ),
        ],
      ),
    );
  }
}
