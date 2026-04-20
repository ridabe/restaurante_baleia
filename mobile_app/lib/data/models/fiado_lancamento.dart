class FiadoLancamento {
  final int id;
  final int clienteId;
  final double valor;
  final String tipo;
  final String? descricao;
  final DateTime dataRegistro;

  const FiadoLancamento({
    required this.id,
    required this.clienteId,
    required this.valor,
    required this.tipo,
    required this.descricao,
    required this.dataRegistro,
  });

  /// Converte payload JSON para entidade de histórico de fiado.
  factory FiadoLancamento.fromJson(Map<String, dynamic> json) {
    return FiadoLancamento(
      id: json['id'] as int,
      clienteId: json['cliente_id'] as int,
      valor: (json['valor'] as num?)?.toDouble() ?? 0,
      tipo: json['tipo'] as String? ?? 'debito',
      descricao: json['descricao'] as String?,
      dataRegistro: DateTime.parse(json['data_registro'] as String),
    );
  }

  /// Converte entidade para mapa serializável em disco.
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'cliente_id': clienteId,
      'valor': valor,
      'tipo': tipo,
      'descricao': descricao,
      'data_registro': dataRegistro.toIso8601String(),
    };
  }
}
