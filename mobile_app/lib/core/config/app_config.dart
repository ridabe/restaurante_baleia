import 'package:flutter_dotenv/flutter_dotenv.dart';

class AppConfig {
  /// URL pública do projeto Supabase.
  static String get supabaseUrl => dotenv.env['SUPABASE_URL'] ?? '';

  /// Chave anônima do Supabase usada no app mobile.
  static String get supabaseAnonKey => dotenv.env['SUPABASE_ANON_KEY'] ?? '';

  /// URL de conexão SQL (reservada para integrações futuras).
  static String get databaseUrl => dotenv.env['DATABASE_URL'] ?? '';

  /// Controla se o app exige autenticação do Supabase para entrar.
  static bool get requireAuth {
    final raw = (dotenv.env['REQUIRE_AUTH'] ?? 'false').toLowerCase();
    return raw == '1' || raw == 'true' || raw == 'yes';
  }
}
