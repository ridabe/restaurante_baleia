import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/utils/currency_formatter.dart';
import '../../routes/app_routes.dart';
import '../../shared/widgets/campo_busca.dart';
import '../../shared/widgets/error_widget_custom.dart';
import '../../shared/widgets/loading_widget.dart';
import 'fiado_controller.dart';

class FiadoPage extends ConsumerStatefulWidget {
  const FiadoPage({super.key});

  @override
  ConsumerState<FiadoPage> createState() => _FiadoPageState();
}

class _FiadoPageState extends ConsumerState<FiadoPage> {
  final _searchController = TextEditingController();

  /// Aplica filtro de clientes pelo nome.
  void _search() {
    ref.read(fiadoControllerProvider.notifier).load(search: _searchController.text);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(fiadoControllerProvider);
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: CampoBusca(controller: _searchController, onSearch: _search, hint: 'Buscar cliente'),
        ),
        Expanded(
          child: state.when(
            loading: () => const LoadingWidget(message: 'Carregando clientes...'),
            error: (error, _) => ErrorWidgetCustom(
              message: 'Erro no fiado: $error',
              onRetry: () => ref.read(fiadoControllerProvider.notifier).load(),
            ),
            data: (clientes) => ListView.builder(
              itemCount: clientes.length,
              itemBuilder: (context, index) {
                final c = clientes[index];
                return Card(
                  margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                  child: ListTile(
                    title: Text(c.nome),
                    subtitle: Text(c.telefone ?? 'Sem telefone'),
                    trailing: Text(
                      CurrencyFormatter.brl(c.dividaAtual),
                      style: TextStyle(
                        color: c.devedor ? Colors.red : Colors.green,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    onTap: () => Navigator.pushNamed(
                      context,
                      AppRoutes.clienteDetail,
                      arguments: c,
                    ),
                  ),
                );
              },
            ),
          ),
        ),
      ],
    );
  }
}
