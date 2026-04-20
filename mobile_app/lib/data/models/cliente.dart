class Cliente {
  final int id;
  final String nome;
  final String? telefone;
  final String? email;
  final double dividaAtual;

  const Cliente({
    required this.id,
    required this.nome,
    required this.telefone,
    required this.email,
    required this.dividaAtual,
  });

  bool get devedor => dividaAtual > 0;

  /// Converte payload JSON do Supabase para entidade Cliente.
  factory Cliente.fromJson(Map<String, dynamic> json) {
    return Cliente(
      id: json['id'] as int,
      nome: json['nome'] as String? ?? '',
      telefone: json['telefone'] as String?,
      email: json['email'] as String?,
      dividaAtual: (json['divida_atual'] as num?)?.toDouble() ?? 0,
    );
  }

  /// Converte entidade para mapa serializável em cache local.
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nome': nome,
      'telefone': telefone,
      'email': email,
      'divida_atual': dividaAtual,
    };
  }
}
