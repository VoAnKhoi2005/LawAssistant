import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../state/documents_view_model.dart';
import '../widgets/documents_view.dart';

class DocumentsPage extends StatelessWidget {
  const DocumentsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => DocumentsViewModel(),
      child: Consumer<DocumentsViewModel>(
        builder: (_, viewModel, __) => DocumentsView(viewModel: viewModel),
      ),
    );
  }
}
