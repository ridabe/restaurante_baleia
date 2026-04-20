class DashboardResumo {
  final double entradasDia;
  final double saidasDia;
  final double saldoDia;
  final double totalFiado;
  final int clientesDevedores;
  final int estoqueBaixo;

  const DashboardResumo({
    required this.entradasDia,
    required this.saidasDia,
    required this.saldoDia,
    required this.totalFiado,
    required this.clientesDevedores,
    required this.estoqueBaixo,
  });

  /// Cria resumo a partir de mapa agregado.
  factory DashboardResumo.fromJson(Map<String, dynamic> json) {
    return DashboardResumo(
      entradasDia: (json['entradas_dia'] as num?)?.toDouble() ?? 0,
      saidasDia: (json['saidas_dia'] as num?)?.toDouble() ?? 0,
      saldoDia: (json['saldo_dia'] as num?)?.toDouble() ?? 0,
      totalFiado: (json['total_fiado'] as num?)?.toDouble() ?? 0,
      clientesDevedores: json['clientes_devedores'] as int? ?? 0,
      estoqueBaixo: json['estoque_baixo'] as int? ?? 0,
    );
  }

  /// Converte resumo para cache local.
  Map<String, dynamic> toJson() {
    return {
      'entradas_dia': entradasDia,
      'saidas_dia': saidasDia,
      'saldo_dia': saldoDia,
      'total_fiado': totalFiado,
      'clientes_devedores': clientesDevedores,
      'estoque_baixo': estoqueBaixo,
    };
  }
}
