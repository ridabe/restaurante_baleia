import 'package:flutter_dotenv/flutter_dotenv.dart';

import '../../services/supabase_service.dart';

class EnvLoader {
  /// Carrega .env e inicializa o client do Supabase.
  static Future<void> initialize() async {
    await dotenv.load();
    await SupabaseService.initialize();
  }
}
