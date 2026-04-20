import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

class LocalCache {
  static const String _prefix = 'cache_';

  /// Salva um objeto serializável em arquivo local para fallback offline.
  static Future<void> write(String key, Map<String, dynamic> data) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('$_prefix$key', jsonEncode(data));
  }

  /// Lê um objeto de cache local; retorna null quando inexistente.
  static Future<Map<String, dynamic>?> read(String key) async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString('$_prefix$key');
    if (raw == null || raw.isEmpty) {
      return null;
    }
    return jsonDecode(raw) as Map<String, dynamic>;
  }
}
