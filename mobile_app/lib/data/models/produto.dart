class Produto {
  final int id;
  final String codigo;
  final String nome;
  final double preco;
  final int quantidade;
  final int estoqueMinimo;
  final String? categoria;

  const Produto({
    required this.id,
    required this.codigo,
    required this.nome,
    required this.preco,
    required this.quantidade,
    required this.estoqueMinimo,
    required this.categoria,
  });

  bool get estoqueBaixo => quantidade <= estoqueMinimo;

  /// Converte payload JSON do Supabase para entidade de domínio.
  factory Produto.fromJson(Map<String, dynamic> json) {
    return Produto(
      id: json['id'] as int,
      codigo: json['codigo'] as String? ?? '',
      nome: json['nome'] as String? ?? '',
      preco: (json['preco'] as num?)?.toDouble() ?? 0,
      quantidade: json['quantidade'] as int? ?? 0,
      estoqueMinimo: json['estoque_minimo'] as int? ?? 0,
      categoria: json['categoria'] as String?,
    );
  }

  /// Converte entidade para mapa serializável de cache local.
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'codigo': codigo,
      'nome': nome,
      'preco': preco,
      'quantidade': quantidade,
      'estoque_minimo': estoqueMinimo,
      'categoria': categoria,
    };
  }
}
