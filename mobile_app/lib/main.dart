import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'app.dart';
import 'core/env/env_loader.dart';

/// Inicializa variáveis de ambiente e dependências globais.
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await EnvLoader.initialize();
  runApp(const ProviderScope(child: BaleiaMobileApp()));
}
