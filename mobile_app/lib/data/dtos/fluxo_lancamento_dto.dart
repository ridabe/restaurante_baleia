class FluxoLancamentoDto {
  final String tipo;
  final double valor;
  final String descricao;
  final String? meioPagamento;
  final int? tipoDespesaId;

  const FluxoLancamentoDto({
    required this.tipo,
    required this.valor,
    required this.descricao,
    this.meioPagamento,
    this.tipoDespesaId,
  });

  /// Converte DTO para payload de lançamento no fluxo de caixa.
  Map<String, dynamic> toJson() {
    return {
      'tipo': tipo,
      'valor': valor,
      'descricao': descricao,
      'meio_pagamento': meioPagamento,
      'tipo_despesa_id': tipoDespesaId,
      'data_registro': DateTime.now().toIso8601String(),
    };
  }
}
