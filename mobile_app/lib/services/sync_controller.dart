import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/datasources/supabase_datasource.dart';
import 'sync_service.dart';

final syncServiceProvider = Provider((ref) => SyncService(SupabaseDatasource()));

final syncControllerProvider = StateNotifierProvider<SyncController, AsyncValue<int>>(
  (ref) => SyncController(ref.read(syncServiceProvider)),
);

class SyncController extends StateNotifier<AsyncValue<int>> {
  final SyncService _service;

  SyncController(this._service) : super(const AsyncData(0));

  Future<int> sync() async {
    state = const AsyncLoading();
    final result = await AsyncValue.guard(() => _service.sync());
    state = result;
    return result.value ?? 0;
  }
}

