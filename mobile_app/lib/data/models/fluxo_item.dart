class FluxoItem {
  final int id;
  final String tipo;
  final String? meioPagamento;
  final double valor;
  final String? descricao;
  final DateTime dataRegistro;
  final double? saldoMomento;
  final int? tipoDespesaId;

  const FluxoItem({
    required this.id,
    required this.tipo,
    required this.meioPagamento,
    required this.valor,
    required this.descricao,
    required this.dataRegistro,
    required this.saldoMomento,
    required this.tipoDespesaId,
  });

  /// Converte payload JSON para item de fluxo de caixa.
  factory FluxoItem.fromJson(Map<String, dynamic> json) {
    return FluxoItem(
      id: json['id'] as int,
      tipo: json['tipo'] as String? ?? 'saida',
      meioPagamento: json['meio_pagamento'] as String?,
      valor: (json['valor'] as num?)?.toDouble() ?? 0,
      descricao: json['descricao'] as String?,
      dataRegistro: DateTime.parse(json['data_registro'] as String),
      saldoMomento: (json['saldo_momento'] as num?)?.toDouble(),
      tipoDespesaId: json['tipo_despesa_id'] as int?,
    );
  }

  /// Converte entidade para mapa serializável em cache local.
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'tipo': tipo,
      'meio_pagamento': meioPagamento,
      'valor': valor,
      'descricao': descricao,
      'data_registro': dataRegistro.toIso8601String(),
      'saldo_momento': saldoMomento,
      'tipo_despesa_id': tipoDespesaId,
    };
  }
}
