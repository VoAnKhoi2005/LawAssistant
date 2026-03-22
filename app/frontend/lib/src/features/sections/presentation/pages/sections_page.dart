import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../state/sections_view_model.dart';
import '../widgets/sections_view.dart';

class SectionsPage extends StatelessWidget {
  const SectionsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => SectionsViewModel(),
      child: Consumer<SectionsViewModel>(
        builder: (_, viewModel, __) => SectionsView(viewModel: viewModel),
      ),
    );
  }
}
