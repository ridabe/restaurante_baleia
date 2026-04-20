import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/config/app_config.dart';
import '../../modules/dashboard/dashboard_page.dart';
import '../../modules/dashboard/dashboard_controller.dart';
import '../../modules/estoque/estoque_page.dart';
import '../../modules/estoque/estoque_controller.dart';
import '../../modules/fiado/fiado_page.dart';
import '../../modules/fiado/fiado_controller.dart';
import '../../modules/fluxo_caixa/fluxo_page.dart';
import '../../modules/fluxo_caixa/fluxo_controller.dart';
import '../../modules/auth/auth_controller.dart';
import '../../core/utils/outbox_store.dart';
import '../../services/sync_controller.dart';

class AppShell extends ConsumerStatefulWidget {
  const AppShell({super.key});

  @override
  ConsumerState<AppShell> createState() => _AppShellState();
}

class _AppShellState extends ConsumerState<AppShell> {
  int _index = 0;

  final List<Widget> _pages = const [
    DashboardPage(),
    EstoquePage(),
    FiadoPage(),
    FluxoPage(),
  ];

  final List<NavigationDestination> _destinations = const [
    NavigationDestination(icon: Icon(Icons.dashboard_outlined), selectedIcon: Icon(Icons.dashboard), label: 'Dashboard'),
    NavigationDestination(icon: Icon(Icons.inventory_2_outlined), selectedIcon: Icon(Icons.inventory_2), label: 'Estoque'),
    NavigationDestination(icon: Icon(Icons.people_outline), selectedIcon: Icon(Icons.people), label: 'Clientes'),
    NavigationDestination(icon: Icon(Icons.attach_money_outlined), selectedIcon: Icon(Icons.attach_money), label: 'Fluxo'),
  ];

  /// Atualiza o índice selecionado da navegação inferior.
  void _onTap(int index) {
    setState(() => _index = index);
    Future.microtask(() => _reloadFor(index));
  }

  Future<void> _reloadFor(int index) async {
    if (index == 0) {
      await ref.read(dashboardControllerProvider.notifier).load();
      return;
    }
    if (index == 1) {
      await ref.read(estoqueControllerProvider.notifier).load();
      return;
    }
    if (index == 2) {
      await ref.read(fiadoControllerProvider.notifier).load();
      return;
    }
    if (index == 3) {
      await ref.read(fluxoControllerProvider.notifier).load();
      return;
    }
  }

  Future<void> _reloadAll() async {
    await Future.wait([
      ref.read(dashboardControllerProvider.notifier).load(),
      ref.read(estoqueControllerProvider.notifier).load(),
      ref.read(fiadoControllerProvider.notifier).load(),
      ref.read(fluxoControllerProvider.notifier).load(),
    ]);
  }

  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(syncControllerProvider.notifier).sync());
  }

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.sizeOf(context).width;
    final isWide = width >= 900;

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Image.asset('assets/images/logo_baleia.png', height: 28),
            const SizedBox(width: 10),
            const Text('Bar do Baleia'),
          ],
        ),
        actions: [
          IconButton(
            onPressed: () async {
              await _reloadAll();
              if (!context.mounted) return;
              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Dados atualizados.')));
            },
            icon: const Icon(Icons.refresh),
            tooltip: 'Atualizar dados',
          ),
          IconButton(
            onPressed: () async {
              final synced = await ref.read(syncControllerProvider.notifier).sync();
              final pending = await OutboxStore.count();
              await _reloadAll();
              if (!context.mounted) return;
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Sincronizado: $synced | Pendentes: $pending')),
              );
            },
            icon: const Icon(Icons.sync),
            tooltip: 'Sincronizar pendências',
          ),
          if (AppConfig.requireAuth)
            IconButton(
              onPressed: () async {
                await ref.read(authControllerProvider).signOut();
              },
              icon: const Icon(Icons.logout),
              tooltip: 'Sair',
            ),
        ],
      ),
      body: isWide
          ? Row(
              children: [
                NavigationRail(
                  selectedIndex: _index,
                  onDestinationSelected: _onTap,
                  labelType: NavigationRailLabelType.all,
                  destinations: _destinations
                      .map(
                        (d) => NavigationRailDestination(
                          icon: d.icon,
                          selectedIcon: d.selectedIcon,
                          label: Text(d.label),
                        ),
                      )
                      .toList(),
                ),
                const VerticalDivider(width: 1),
                Expanded(child: _pages[_index]),
              ],
            )
          : _pages[_index],
      bottomNavigationBar: isWide
          ? null
          : NavigationBar(
              selectedIndex: _index,
              onDestinationSelected: _onTap,
              destinations: _destinations,
            ),
    );
  }
}
