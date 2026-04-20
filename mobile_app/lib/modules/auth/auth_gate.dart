import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/config/app_config.dart';
import '../../shared/layout/app_shell.dart';
import '../../shared/widgets/loading_widget.dart';
import 'auth_controller.dart';
import 'login_page.dart';

class AuthGate extends ConsumerWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (!AppConfig.requireAuth) {
      return const AppShell();
    }

    final session = ref.watch(authSessionProvider);
    return session.when(
      loading: () => const Scaffold(body: LoadingWidget(message: 'Inicializando sessão...')),
      error: (error, _) => Scaffold(body: Center(child: Text('Erro de sessão: $error'))),
      data: (session) {
        if (session == null) {
          return const LoginPage();
        }
        return const AppShell();
      },
    );
  }
}
