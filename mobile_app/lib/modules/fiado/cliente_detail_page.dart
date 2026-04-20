import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/utils/currency_formatter.dart';
import '../../data/models/cliente.dart';
import '../../data/models/fiado_lancamento.dart';
import 'fiado_controller.dart';

class ClienteDetailPage extends ConsumerStatefulWidget {
  final Cliente cliente;

  const ClienteDetailPage({super.key, required this.cliente});

  @override
  ConsumerState<ClienteDetailPage> createState() => _ClienteDetailPageState();
}

class _ClienteDetailPageState extends ConsumerState<ClienteDetailPage> {
  final _valorController = TextEditingController();
  final _descricaoController = TextEditingController(text: 'Pagamento via mobile');

  /// Exibe diálogo para registrar pagamento do fiado.
  Future<void> _registrarPagamento() async {
    final valor = double.tryParse(_valorController.text.replaceAll(',', '.'));
    if (valor == null || valor <= 0) return;
    final queued = await ref.read(fiadoControllerProvider.notifier).pagarFiado(
          clienteId: widget.cliente.id,
          valor: valor,
          descricao: _descricaoController.text,
        );
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(queued ? 'Sem conexão. Pagamento pendente para sincronização.' : 'Pagamento registrado com sucesso')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.cliente.nome)),
      body: FutureBuilder<List<FiadoLancamento>>(
        future: ref.read(fiadoControllerProvider.notifier).getHistorico(widget.cliente.id),
        builder: (context, snapshot) {
          final historico = snapshot.data ?? [];
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Dívida Atual: ${CurrencyFormatter.brl(widget.cliente.dividaAtual)}'),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _valorController,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: const InputDecoration(labelText: 'Valor do pagamento'),
                      ),
                      const SizedBox(height: 8),
                      TextField(
                        controller: _descricaoController,
                        decoration: const InputDecoration(labelText: 'Descrição'),
                      ),
                      const SizedBox(height: 12),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          onPressed: _registrarPagamento,
                          child: const Text('Registrar pagamento'),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              const Text('Histórico', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              ...historico.map(
                (h) => Card(
                  child: ListTile(
                    title: Text('${h.tipo.toUpperCase()} - ${CurrencyFormatter.brl(h.valor)}'),
                    subtitle: Text(h.descricao ?? '-'),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
