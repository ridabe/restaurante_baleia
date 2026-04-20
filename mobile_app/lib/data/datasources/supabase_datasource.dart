import 'package:supabase_flutter/supabase_flutter.dart';

import '../../data/dtos/fluxo_lancamento_dto.dart';
import '../../data/dtos/pagamento_fiado_dto.dart';
import '../../services/supabase_service.dart';

class SupabaseDatasource {
  final SupabaseClient _client = SupabaseService.client;

  static final RegExp _clienteIdRegex1 = RegExp(r'\bcliente\s*#?\s*:?\s*(\d+)\b', caseSensitive: false);
  static final RegExp _clienteIdRegex2 = RegExp(r'\bcliente(\d+)\b', caseSensitive: false);

  String _toTimestampWithoutOffset(DateTime value) {
    final local = DateTime(value.year, value.month, value.day, value.hour, value.minute, value.second, value.millisecond);
    return local.toIso8601String();
  }

  ({String start, String end}) _todayRange() {
    final now = DateTime.now();
    final start = DateTime(now.year, now.month, now.day);
    final end = DateTime(now.year, now.month, now.day, 23, 59, 59);
    return (start: _toTimestampWithoutOffset(start), end: _toTimestampWithoutOffset(end));
  }

  int? _extractClienteIdFromDescricao(String? descricao) {
    if (descricao == null || descricao.isEmpty) return null;
    final m1 = _clienteIdRegex1.firstMatch(descricao);
    if (m1 != null) {
      return int.tryParse(m1.group(1) ?? '');
    }
    final m2 = _clienteIdRegex2.firstMatch(descricao);
    if (m2 != null) {
      return int.tryParse(m2.group(1) ?? '');
    }
    return null;
  }

  String _humanizeDescricaoComCliente(String descricao, String clienteNome, {double? valor}) {
    final lower = descricao.toLowerCase();
    if (lower.contains('pagamento') && (lower.contains('fiado') || lower.contains('dívida') || lower.contains('divida'))) {
      final pago = valor ?? 0;
      return 'Pagamento de dívida | Cliente: $clienteNome | Pago: R\$ ${pago.toStringAsFixed(2)}';
    }
    return descricao
        .replaceAllMapped(_clienteIdRegex1, (_) => 'Cliente: $clienteNome')
        .replaceAllMapped(_clienteIdRegex2, (_) => 'Cliente: $clienteNome');
  }

  Future<List<Map<String, dynamic>>> _enrichMovimentosComNomeCliente(List<Map<String, dynamic>> rows) async {
    final ids = <int>{};
    for (final r in rows) {
      final descricao = r['descricao']?.toString();
      final id = _extractClienteIdFromDescricao(descricao);
      if (id != null) ids.add(id);
    }
    if (ids.isEmpty) return rows;

    final clientes = await _client.from('clientes').select('id, nome').inFilter('id', ids.toList());
    final byId = <int, String>{};
    for (final c in clientes) {
      final id = c['id'] as int?;
      final nome = c['nome']?.toString();
      if (id != null && nome != null && nome.isNotEmpty) {
        byId[id] = nome;
      }
    }

    return rows.map((r) {
      final descricao = r['descricao']?.toString();
      final id = _extractClienteIdFromDescricao(descricao);
      if (descricao != null && id != null && byId.containsKey(id)) {
        final valor = (r['valor'] as num?)?.toDouble();
        return {...r, 'descricao': _humanizeDescricaoComCliente(descricao, byId[id]!, valor: valor)};
      }
      return r;
    }).toList();
  }

  /// Busca produtos de estoque ordenados por nome.
  Future<List<Map<String, dynamic>>> fetchProdutos({String? search}) async {
    var query = _client.from('produtos').select();
    if (search != null && search.trim().isNotEmpty) {
      final term = search.trim();
      query = query.or('nome.ilike.%$term%,codigo.ilike.%$term%');
    }
    final data = await query.order('nome');
    return List<Map<String, dynamic>>.from(data);
  }

  /// Atualiza quantidade do produto para ajuste administrativo.
  Future<void> updateProdutoQuantidade({required int produtoId, required int quantidade}) async {
    await _client.from('produtos').update({'quantidade': quantidade}).eq('id', produtoId);
  }

  /// Busca clientes para módulo de fiado.
  Future<List<Map<String, dynamic>>> fetchClientes({String? search}) async {
    var query = _client.from('clientes').select();
    if (search != null && search.trim().isNotEmpty) {
      query = query.ilike('nome', '%${search.trim()}%');
    }
    final data = await query.order('nome');
    return List<Map<String, dynamic>>.from(data);
  }

  /// Busca histórico do fiado de um cliente.
  Future<List<Map<String, dynamic>>> fetchHistoricoFiado(int clienteId) async {
    final data = await _client
        .from('fiados')
        .select()
        .eq('cliente_id', clienteId)
        .order('data_registro', ascending: false);
    return List<Map<String, dynamic>>.from(data);
  }

  /// Registra pagamento no fiado e cria entrada no fluxo de caixa.
  Future<void> registrarPagamentoFiado(PagamentoFiadoDto dto) async {
    try {
      await _client.rpc(
        'registrar_pagamento_fiado',
        params: {
          'p_cliente_id': dto.clienteId,
          'p_valor': dto.valor,
          'p_descricao': dto.descricao,
        },
      );
      return;
    } catch (_) {}

    final clienteData = await _client
        .from('clientes')
        .select('divida_atual, nome')
        .eq('id', dto.clienteId)
        .maybeSingle();
    final dividaAtual = (clienteData?['divida_atual'] as num?)?.toDouble() ?? 0;
    final clienteNome = clienteData?['nome']?.toString() ?? '';
    final novaDivida = (dividaAtual - dto.valor).clamp(0, double.infinity).toDouble();

    var descricaoFluxo =
        'Pagamento de dívida | Cliente: $clienteNome | Pago: R\$ ${dto.valor.toStringAsFixed(2)} | Saldo restante: R\$ ${novaDivida.toStringAsFixed(2)}';
    if (dto.meioPagamento.trim().isNotEmpty) {
      descricaoFluxo += ' | Meio: ${dto.meioPagamento}';
    }
    if (dto.descricao.trim().isNotEmpty) {
      descricaoFluxo += ' | Obs: ${dto.descricao.trim()}';
    }

    await _client.from('fiados').insert(dto.toJsonFiado());
    await _client.from('clientes').update({'divida_atual': novaDivida}).eq('id', dto.clienteId);
    await _client.from('fluxo_caixa').insert({
      'tipo': 'entrada',
      'valor': dto.valor,
      'descricao': descricaoFluxo,
      'meio_pagamento': dto.meioPagamento,
      'data_registro': DateTime.now().toIso8601String(),
    });
  }

  /// Busca itens do fluxo de caixa por período.
  Future<List<Map<String, dynamic>>> fetchFluxo({DateTime? inicio, DateTime? fim}) async {
    var query = _client.from('fluxo_caixa').select();
    if (inicio != null) {
      query = query.gte('data_registro', inicio.toIso8601String());
    }
    if (fim != null) {
      query = query.lte('data_registro', fim.toIso8601String());
    }
    final data = await query.order('data_registro', ascending: false);
    final rows = List<Map<String, dynamic>>.from(data);
    return _enrichMovimentosComNomeCliente(rows);
  }

  /// Insere lançamento manual de entrada ou saída no fluxo.
  Future<void> registrarLancamentoFluxo(FluxoLancamentoDto dto) async {
    try {
      await _client.rpc(
        'registrar_lancamento_fluxo',
        params: {
          'p_tipo': dto.tipo,
          'p_valor': dto.valor,
          'p_descricao': dto.descricao,
          'p_meio_pagamento': dto.meioPagamento ?? 'indefinido',
          'p_tipo_despesa_id': dto.tipoDespesaId,
        },
      );
      return;
    } catch (_) {}
    await _client.from('fluxo_caixa').insert(dto.toJson());
  }

  /// Monta agregados do dashboard a partir de consultas reais do banco.
  Future<Map<String, dynamic>> fetchDashboardResumo() async {
    final range = _todayRange();

    final fluxoHoje = await _client
        .from('fluxo_caixa')
        .select('tipo, valor')
        .gte('data_registro', range.start)
        .lte('data_registro', range.end);

    final clientes = await _client.from('clientes').select('id, divida_atual').gt('divida_atual', 0);
    final produtos = await _client.from('produtos').select('quantidade, estoque_minimo');

    double entradas = 0;
    double saidas = 0;
    for (final item in fluxoHoje) {
      final tipo = item['tipo'] as String? ?? '';
      final valor = (item['valor'] as num?)?.toDouble() ?? 0;
      if (tipo == 'entrada') {
        entradas += valor;
      } else {
        saidas += valor;
      }
    }

    double fiadoTotal = 0;
    for (final c in clientes) {
      fiadoTotal += (c['divida_atual'] as num?)?.toDouble() ?? 0;
    }
    var estoqueBaixo = 0;
    for (final p in produtos) {
      final qtd = p['quantidade'] as int? ?? 0;
      final minimo = p['estoque_minimo'] as int? ?? 0;
      if (qtd <= minimo) {
        estoqueBaixo += 1;
      }
    }

    return {
      'entradas_dia': entradas,
      'saidas_dia': saidas,
      'saldo_dia': entradas - saidas,
      'total_fiado': fiadoTotal,
      'clientes_devedores': clientes.length,
      'estoque_baixo': estoqueBaixo,
    };
  }

  /// Consolida série de entradas x saídas dos últimos 7 dias.
  Future<List<Map<String, dynamic>>> fetchSerieFluxo7Dias() async {
    final inicio = DateTime.now().subtract(const Duration(days: 6));
    final data = await _client
        .from('fluxo_caixa')
        .select('tipo, valor, data_registro')
        .gte('data_registro', _toTimestampWithoutOffset(DateTime(inicio.year, inicio.month, inicio.day)))
        .order('data_registro');

    final Map<String, Map<String, double>> bucket = {};
    for (final row in data) {
      final date = DateTime.parse(row['data_registro'] as String);
      final dayKey = DateTime(date.year, date.month, date.day).toIso8601String();
      bucket.putIfAbsent(dayKey, () => {'entradas': 0, 'saidas': 0});
      final tipo = row['tipo'] as String? ?? '';
      final valor = (row['valor'] as num?)?.toDouble() ?? 0;
      if (tipo == 'entrada') {
        bucket[dayKey]!['entradas'] = bucket[dayKey]!['entradas']! + valor;
      } else {
        bucket[dayKey]!['saidas'] = bucket[dayKey]!['saidas']! + valor;
      }
    }

    final entries = bucket.entries.toList()..sort((a, b) => a.key.compareTo(b.key));
    return entries
        .map((entry) => {'dia': entry.key, 'entradas': entry.value['entradas'] ?? 0, 'saidas': entry.value['saidas'] ?? 0})
        .toList();
  }

  /// Consolida despesas por categoria usando `tipo_despesa_id`.
  Future<List<Map<String, dynamic>>> fetchDespesasPorCategoria() async {
    try {
      final data = await _client
          .from('fluxo_caixa')
          .select('valor, tipo_despesa:tipos_despesa(nome)')
          .eq('tipo', 'saida')
          .not('tipo_despesa_id', 'is', null);

      final Map<String, double> categorias = {};
      for (final row in data) {
        final nome = (row['tipo_despesa'] as Map?)?['nome']?.toString() ?? 'Sem categoria';
        categorias[nome] = (categorias[nome] ?? 0) + ((row['valor'] as num?)?.toDouble() ?? 0);
      }

      final list = categorias.entries.map((e) => {'categoria': e.key, 'valor': e.value}).toList();
      list.sort((a, b) => (b['valor'] as double).compareTo(a['valor'] as double));
      return list;
    } catch (_) {
      final data = await _client
          .from('fluxo_caixa')
          .select('valor, tipo_despesa_id')
          .eq('tipo', 'saida')
          .not('tipo_despesa_id', 'is', null);

      final Map<int, double> categorias = {};
      for (final row in data) {
        final categoria = row['tipo_despesa_id'] as int;
        categorias[categoria] = (categorias[categoria] ?? 0) + ((row['valor'] as num?)?.toDouble() ?? 0);
      }

      return categorias.entries.map((entry) => {'categoria': entry.key.toString(), 'valor': entry.value}).toList();
    }
  }

  /// Lista as últimas movimentações do fluxo de caixa.
  Future<List<Map<String, dynamic>>> fetchUltimasMovimentacoes({int limit = 10}) async {
    final data = await _client
        .from('fluxo_caixa')
        .select('id, tipo, valor, descricao, data_registro')
        .order('data_registro', ascending: false)
        .limit(limit);
    final rows = List<Map<String, dynamic>>.from(data);
    return _enrichMovimentosComNomeCliente(rows);
  }

  /// Lista produtos com estoque abaixo do mínimo.
  Future<List<Map<String, dynamic>>> fetchAlertasEstoqueBaixo({int limit = 10}) async {
    final data = await _client
        .from('produtos')
        .select('id, nome, quantidade, estoque_minimo')
        .order('quantidade');
    final items = List<Map<String, dynamic>>.from(data);
    final filtered = items.where((p) {
      final qtd = p['quantidade'] as int? ?? 0;
      final minimo = p['estoque_minimo'] as int? ?? 0;
      return qtd <= minimo;
    }).toList();
    return filtered.take(limit).toList();
  }

  /// Lista os maiores devedores de fiado.
  Future<List<Map<String, dynamic>>> fetchGestaoFiado({int limit = 6}) async {
    final data = await _client
        .from('clientes')
        .select('id, nome, telefone, divida_atual')
        .gt('divida_atual', 0)
        .order('divida_atual', ascending: false)
        .limit(limit);
    return List<Map<String, dynamic>>.from(data);
  }

  /// Consolida produtos mais vendidos do dia a partir das vendas e itens de venda.
  Future<List<Map<String, dynamic>>> fetchProdutosMaisVendidosDia({int limit = 10}) async {
    final range = _todayRange();
    final vendas = await _client
        .from('vendas')
        .select('id')
        .gte('data_venda', range.start)
        .lte('data_venda', range.end);

    final vendaIds = List<Map<String, dynamic>>.from(vendas).map((e) => e['id'] as int).toList();
    if (vendaIds.isEmpty) {
      return [];
    }

    List<Map<String, dynamic>> itens;
    try {
      final data = await _client
          .from('itens_venda')
          .select('produto_id, quantidade, subtotal, produto:produtos(nome)')
          .inFilter('venda_id', vendaIds);
      itens = List<Map<String, dynamic>>.from(data);
    } catch (_) {
      final data = await _client
          .from('itens_venda')
          .select('produto_id, quantidade, subtotal')
          .inFilter('venda_id', vendaIds);
      itens = List<Map<String, dynamic>>.from(data);
    }

    final Map<int, ({int qtd, double total, String? nome})> acc = {};
    for (final item in itens) {
      final produtoId = item['produto_id'] as int;
      final qtd = item['quantidade'] as int? ?? 0;
      final total = (item['subtotal'] as num?)?.toDouble() ?? 0;
      final nome = (item['produto'] as Map?)?['nome']?.toString();
      final current = acc[produtoId];
      acc[produtoId] = (
        qtd: (current?.qtd ?? 0) + qtd,
        total: (current?.total ?? 0) + total,
        nome: nome ?? current?.nome,
      );
    }

    final missingIds = acc.entries.where((e) => (e.value.nome ?? '').isEmpty).map((e) => e.key).toList();
    if (missingIds.isNotEmpty) {
      final produtos = await _client.from('produtos').select('id, nome').inFilter('id', missingIds);
      final byId = {for (final p in produtos) p['id'] as int: p['nome']?.toString() ?? ''};
      for (final id in missingIds) {
        final current = acc[id]!;
        acc[id] = (qtd: current.qtd, total: current.total, nome: byId[id] ?? '');
      }
    }

    final list = acc.entries
        .map(
          (e) => {
            'produto_id': e.key,
            'nome': e.value.nome ?? '',
            'quantidade': e.value.qtd,
            'total': e.value.total,
          },
        )
        .toList();
    list.sort((a, b) => (b['quantidade'] as int).compareTo(a['quantidade'] as int));
    return list.take(limit).toList();
  }
}
