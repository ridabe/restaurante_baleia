class EstoqueAlerta {
  final int produtoId;
  final String nome;
  final int atual;
  final int minimo;

  const EstoqueAlerta({
    required this.produtoId,
    required this.nome,
    required this.atual,
    required this.minimo,
  });
}

