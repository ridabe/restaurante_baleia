class DashboardSerie {
  final DateTime dia;
  final double entradas;
  final double saidas;

  const DashboardSerie({
    required this.dia,
    required this.entradas,
    required this.saidas,
  });

  /// Converte mapa agregado diário em série para gráfico.
  factory DashboardSerie.fromJson(Map<String, dynamic> json) {
    return DashboardSerie(
      dia: DateTime.parse(json['dia'] as String),
      entradas: (json['entradas'] as num?)?.toDouble() ?? 0,
      saidas: (json['saidas'] as num?)?.toDouble() ?? 0,
    );
  }

  /// Converte série para formato serializável.
  Map<String, dynamic> toJson() {
    return {
      'dia': dia.toIso8601String(),
      'entradas': entradas,
      'saidas': saidas,
    };
  }
}
