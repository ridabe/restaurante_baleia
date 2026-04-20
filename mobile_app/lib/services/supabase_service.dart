import 'package:supabase_flutter/supabase_flutter.dart';

import '../core/config/app_config.dart';

class SupabaseService {
  /// Inicializa o SDK do Supabase de forma centralizada.
  static Future<void> initialize() async {
    await Supabase.initialize(
      url: AppConfig.supabaseUrl,
      anonKey: AppConfig.supabaseAnonKey,
    );
  }

  /// Fornece o client singleton para datasources e repositories.
  static SupabaseClient get client => Supabase.instance.client;
}
