import 'package:flutter/material.dart';

import 'core/theme/app_theme.dart';
import 'modules/auth/auth_gate.dart';
import 'routes/app_routes.dart';

class BaleiaMobileApp extends StatelessWidget {
  const BaleiaMobileApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Bar do Baleia Mobile',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.build(),
      onGenerateRoute: AppRoutes.onGenerateRoute,
      home: const AuthGate(),
    );
  }
}
