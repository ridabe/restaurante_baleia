import 'package:flutter/material.dart';

class AppTheme {
  /// Constrói o tema global com identidade visual do Bar do Baleia.
  static ThemeData build() {
    return ThemeData(
      useMaterial3: true,
      primaryColor: Colors.green,
      scaffoldBackgroundColor: Colors.grey[100],
      colorScheme: ColorScheme.fromSeed(seedColor: Colors.green),
      cardTheme: CardThemeData(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
      ),
    );
  }
}
