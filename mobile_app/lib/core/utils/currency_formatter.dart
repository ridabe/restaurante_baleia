import 'package:intl/intl.dart';

class CurrencyFormatter {
  static final NumberFormat _brl = NumberFormat.currency(locale: 'pt_BR', symbol: 'R\$');

  /// Formata valores numéricos para moeda brasileira.
  static String brl(num value) => _brl.format(value);
}
