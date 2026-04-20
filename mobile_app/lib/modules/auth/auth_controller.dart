import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../../services/supabase_service.dart';

final authSessionProvider = StreamProvider<Session?>((ref) async* {
  final auth = SupabaseService.client.auth;
  yield auth.currentSession;
  yield* auth.onAuthStateChange.map((event) => event.session);
});

final authControllerProvider = Provider((ref) => AuthController(SupabaseService.client));

class AuthController {
  final SupabaseClient _client;

  AuthController(this._client);

  Future<void> signInWithPassword({required String email, required String password}) async {
    await _client.auth.signInWithPassword(email: email, password: password);
  }

  Future<void> signOut() async {
    await _client.auth.signOut();
  }
}

