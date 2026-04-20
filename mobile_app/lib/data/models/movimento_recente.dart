class MovimentoRecente {
  final int id;
  final DateTime dataRegistro;
  final String tipo;
  final String descricao;
  final double valor;

  const MovimentoRecente({
    required this.id,
    required this.dataRegistro,
    required this.tipo,
    required this.descricao,
    required this.valor,
  });
}

