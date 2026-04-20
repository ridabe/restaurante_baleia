import 'package:flutter/material.dart';

import '../data/models/cliente.dart';
import '../modules/fiado/cliente_detail_page.dart';

class AppRoutes {
  static const String clienteDetail = '/cliente-detail';

  /// Resolve rotas nomeadas e seus argumentos.
  static Route<dynamic>? onGenerateRoute(RouteSettings settings) {
    switch (settings.name) {
      case clienteDetail:
        final cliente = settings.arguments as Cliente;
        return MaterialPageRoute(builder: (_) => ClienteDetailPage(cliente: cliente));
      default:
        return null;
    }
  }
}
