class PagamentoFiadoDto {
  final int clienteId;
  final double valor;
  final String descricao;
  final String meioPagamento;

  const PagamentoFiadoDto({
    required this.clienteId,
    required this.valor,
    required this.descricao,
    this.meioPagamento = 'DINHEIRO',
  });

  /// Converte DTO para payload de inserção no Supabase.
  Map<String, dynamic> toJsonFiado() {
    return {
      'cliente_id': clienteId,
      'valor': valor,
      'tipo': 'credito',
      'descricao': descricao,
      'data_registro': DateTime.now().toIso8601String(),
    };
  }
}
