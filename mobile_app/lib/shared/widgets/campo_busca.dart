import 'package:flutter/material.dart';

class CampoBusca extends StatelessWidget {
  final TextEditingController controller;
  final VoidCallback onSearch;
  final String hint;

  const CampoBusca({
    super.key,
    required this.controller,
    required this.onSearch,
    required this.hint,
  });

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      textInputAction: TextInputAction.search,
      onSubmitted: (_) => onSearch(),
      decoration: InputDecoration(
        hintText: hint,
        suffixIcon: IconButton(onPressed: onSearch, icon: const Icon(Icons.search)),
      ),
    );
  }
}
