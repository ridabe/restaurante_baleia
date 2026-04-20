import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

class OutboxStore {
  static const String _storageKey = 'outbox_items';

  /// Retorna a quantidade atual de itens pendentes de sincronização.
  static Future<int> count() async {
    final items = await readAll();
    return items.length;
  }

  /// Lê todos os itens pendentes persistidos localmente.
  static Future<List<Map<String, dynamic>>> readAll() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_storageKey);
    if (raw == null || raw.isEmpty) {
      return [];
    }
    final decoded = jsonDecode(raw);
    if (decoded is! List) {
      return [];
    }
    return decoded.map((e) => Map<String, dynamic>.from(e as Map)).toList();
  }

  /// Substitui a fila inteira da outbox por uma nova lista de itens.
  static Future<void> replaceAll(List<Map<String, dynamic>> items) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_storageKey, jsonEncode(items));
  }

  /// Adiciona uma operação pendente na fila para sincronizar depois.
  static Future<void> enqueue({
    required String type,
    required Map<String, dynamic> payload,
  }) async {
    final items = await readAll();
    items.add({
      'id': DateTime.now().microsecondsSinceEpoch.toString(),
      'type': type,
      'payload': payload,
      'created_at': DateTime.now().toIso8601String(),
    });
    await replaceAll(items);
  }
}
