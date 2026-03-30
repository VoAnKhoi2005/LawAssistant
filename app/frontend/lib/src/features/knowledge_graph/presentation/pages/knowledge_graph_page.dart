import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../state/knowledge_graph_view_model.dart';
import '../widgets/knowledge_graph_view.dart';

class KnowledgeGraphPage extends StatelessWidget {
  const KnowledgeGraphPage({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => KnowledgeGraphViewModel(),
      child: Consumer<KnowledgeGraphViewModel>(
        builder: (_, viewModel, __) => KnowledgeGraphView(viewModel: viewModel),
      ),
    );
  }
}
