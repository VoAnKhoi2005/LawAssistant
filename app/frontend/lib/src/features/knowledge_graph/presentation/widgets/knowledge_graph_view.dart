import 'package:flutter/material.dart';
import 'package:graphview/GraphView.dart';

import '../state/knowledge_graph_view_model.dart';

class KnowledgeGraphView extends StatelessWidget {
  const KnowledgeGraphView({super.key, required this.viewModel});

  final KnowledgeGraphViewModel viewModel;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      backgroundColor: colorScheme.surface,
      body: Stack(
        children: [
          Column(
            children: [
              _buildHeader(theme, colorScheme),
              _buildSelectionFlow(theme, colorScheme),
              Expanded(
                child: AnimatedSwitcher(
                  duration: const Duration(milliseconds: 250),
                  child: viewModel.showGraph
                      ? _buildGraphArea(theme, colorScheme)
                      : _buildEmptyState(theme, colorScheme),
                ),
              ),
            ],
          ),
          if (viewModel.showGraph && viewModel.showEditPanel)
            Positioned(
              right: 0,
              top: 0,
              bottom: 0,
              child: _buildEditSidebar(theme, colorScheme),
            ),
        ],
      ),
    );
  }

  Widget _buildHeader(ThemeData theme, ColorScheme colorScheme) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(32, 24, 32, 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'KNOWLEDGE GRAPH EXPLORER',
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    color: colorScheme.onSurfaceVariant.withOpacity(0.7),
                    letterSpacing: 2,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Cơ sở Dữ liệu Luật Dân sự',
                  style: theme.textTheme.headlineLarge?.copyWith(fontSize: 30),
                ),
              ],
            ),
          ),
          Row(
            children: [
              OutlinedButton.icon(
                onPressed: viewModel.handleHistory,
                icon: const Icon(Icons.history, size: 16),
                label: const Text('History'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  side: BorderSide(color: colorScheme.surfaceContainer),
                  backgroundColor: colorScheme.surfaceContainerHigh,
                ),
              ),
              const SizedBox(width: 12),
              IconButton(
                onPressed: viewModel.handleShare,
                icon: const Icon(Icons.share, size: 18),
                style: IconButton.styleFrom(
                  backgroundColor: colorScheme.primary,
                  foregroundColor: Colors.white,
                ),
                tooltip: 'Share graph',
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSelectionFlow(ThemeData theme, ColorScheme colorScheme) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: colorScheme.surfaceContainer),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.02), blurRadius: 4),
        ],
      ),
      child: Row(
        children: [
          _buildStep(
            '1',
            'Select Document',
            colorScheme,
            viewModel.selectedDocument ?? 'Select...',
            () => viewModel.selectDocument('Bộ luật Dân sự 2015'),
          ),
          Icon(
            Icons.arrow_forward,
            size: 14,
            color: colorScheme.outlineVariant.withOpacity(0.5),
          ),
          const SizedBox(width: 16),
          _buildStep(
            '2',
            'Select Section',
            colorScheme,
            viewModel.selectedSection ?? 'Select...',
            () => viewModel.selectSection('Điều 385'),
          ),
        ],
      ),
    );
  }

  Widget _buildStep(
    String number,
    String label,
    ColorScheme colorScheme,
    String value,
    VoidCallback onTap,
  ) {
    return Expanded(
      child: Row(
        children: [
          Container(
            width: 24,
            height: 24,
            decoration: BoxDecoration(
              color: colorScheme.primary.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            alignment: Alignment.center,
            child: Text(
              number,
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w700,
                color: colorScheme.primary,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: InkWell(
              onTap: onTap,
              borderRadius: BorderRadius.circular(8),
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 6,
                ),
                decoration: BoxDecoration(
                  color: Colors.white,
                  border: Border.all(color: colorScheme.surfaceContainer),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        value,
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                          color: colorScheme.onSurfaceVariant,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    Icon(
                      Icons.expand_more,
                      size: 16,
                      color: colorScheme.outlineVariant,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState(ThemeData theme, ColorScheme colorScheme) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: colorScheme.surfaceContainer,
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.hub_outlined,
              size: 40,
              color: colorScheme.outlineVariant,
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'Ready for Relationship Analysis',
            style: theme.textTheme.titleLarge?.copyWith(
              fontSize: 18,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          SizedBox(
            width: 400,
            child: Text(
              'Complete the Document and Section selection above to begin visualizing legal entities.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 14,
                color: colorScheme.onSurfaceVariant,
              ),
            ),
          ),
          const SizedBox(height: 32),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _buildStepIndicator('1', 'Document', colorScheme),
              Container(
                width: 40,
                height: 1,
                margin: const EdgeInsets.symmetric(horizontal: 16),
                color: colorScheme.outlineVariant,
              ),
              _buildStepIndicator('2', 'Section', colorScheme),
            ],
          ),
          const SizedBox(height: 48),
          FilledButton(
            onPressed: viewModel.loadExampleGraph,
            child: const Text('Show Example Graph'),
          ),
        ],
      ),
    );
  }

  Widget _buildStepIndicator(
    String number,
    String label,
    ColorScheme colorScheme,
  ) {
    return Column(
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            border: Border.all(color: colorScheme.outlineVariant),
            shape: BoxShape.circle,
          ),
          alignment: Alignment.center,
          child: Text(
            number,
            style: TextStyle(fontSize: 12, color: colorScheme.outlineVariant),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: TextStyle(
            fontSize: 9,
            fontWeight: FontWeight.w700,
            color: colorScheme.outline,
            letterSpacing: 1,
          ),
        ),
      ],
    );
  }

  Widget _buildGraphArea(ThemeData theme, ColorScheme colorScheme) {
    final graph = Graph()..isTree = false;
    final nodeMap = <String, Node>{};

    // Build nodes
    for (final node in viewModel.graphNodes) {
      final graphNode = Node.Id(node.id);
      nodeMap[node.id] = graphNode;
      graph.addNode(graphNode);
    }

    // Build edges (directed)
    for (final edge in viewModel.graphEdges) {
      final from = nodeMap[edge.from];
      final to = nodeMap[edge.to];
      if (from != null && to != null) {
        graph.addEdge(from, to);
      }
    }

    //Force-directed configuration
    final config = FruchtermanReingoldConfiguration()..iterations = 500;

    return Container(
      decoration: BoxDecoration(color: colorScheme.surfaceContainerLowest),
      child: Stack(
        children: [
          Positioned.fill(
            child: InteractiveViewer(
              constrained: false,
              minScale: 0.3,
              maxScale: 3.0,
              panEnabled: true,
              scaleEnabled: true,
              trackpadScrollCausesScale: true,
              boundaryMargin: const EdgeInsets.all(500),

              child: Padding(
                padding: const EdgeInsets.all(40),
                child: GraphView(
                  graph: graph,

                  //Force-directed algorithm (correct usage)
                  algorithm: FruchtermanReingoldAlgorithm(config),

                  paint: Paint()
                    ..color = colorScheme.outlineVariant
                    ..strokeWidth = 1.6
                    ..style = PaintingStyle.stroke,

                  builder: (node) {
                    final rawId = node.key?.value?.toString();

                    GraphNode? graphNode;
                    try {
                      graphNode = viewModel.graphNodes.firstWhere(
                        (n) => n.id == rawId,
                      );
                    } catch (_) {
                      graphNode = null;
                    }

                    if (graphNode == null || rawId == null) {
                      return const SizedBox.shrink();
                    }

                    final selected = viewModel.selectedNodeId == rawId;

                    return GestureDetector(
                      behavior: HitTestBehavior.translucent,
                      onTap: () => viewModel.selectNode(rawId),
                      child: _GraphNodeChip(
                        node: graphNode,
                        colorScheme: colorScheme,
                        selected: selected,
                      ),
                    );
                  },
                ),
              ),
            ),
          ),

          // Toolbar
          _buildFloatingToolbar(colorScheme),

          // Legend
          Positioned(right: 24, top: 24, child: _buildLegend(colorScheme)),
        ],
      ),
    );
  }

  Widget _buildFloatingToolbar(ColorScheme colorScheme) {
    return Positioned(
      left: 24,
      bottom: 24,
      child: Column(
        children: [
          _buildToolbarButton(
            Icons.zoom_in,
            colorScheme,
            viewModel.handleZoomIn,
          ),
          const SizedBox(height: 8),
          _buildToolbarButton(
            Icons.zoom_out,
            colorScheme,
            viewModel.handleZoomOut,
          ),
          const SizedBox(height: 8),
          _buildToolbarButton(
            Icons.center_focus_strong,
            colorScheme,
            viewModel.handleCenter,
          ),
          const SizedBox(height: 8),
          _buildToolbarButton(
            Icons.edit,
            colorScheme,
            viewModel.toggleEditPanel,
          ),
        ],
      ),
    );
  }

  Widget _buildToolbarButton(
    IconData icon,
    ColorScheme colorScheme,
    VoidCallback onTap,
  ) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        width: 36,
        height: 36,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: colorScheme.surfaceContainer),
          boxShadow: [
            BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 8),
          ],
        ),
        child: Icon(icon, size: 20, color: colorScheme.primary),
      ),
    );
  }

  Widget _buildLegend(ColorScheme colorScheme) {
    Widget legendItem(Color color, String label, IconData icon) {
      return Row(
        children: [
          Container(
            width: 26,
            height: 26,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
            child: Icon(icon, size: 14, color: colorScheme.onPrimaryContainer),
          ),
          const SizedBox(width: 8),
          Text(label, style: TextStyle(color: colorScheme.onSurfaceVariant)),
        ],
      );
    }

    return DecoratedBox(
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.9),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: colorScheme.surfaceContainer),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            legendItem(
              colorScheme.primaryContainer,
              'Subject',
              Icons.account_balance,
            ),
            const SizedBox(width: 12),
            legendItem(colorScheme.tertiaryContainer, 'Object', Icons.gavel),
          ],
        ),
      ),
    );
  }

  Widget _buildEditSidebar(ThemeData theme, ColorScheme colorScheme) {
    final selectedNode = viewModel.selectedNode;
    final relatedEdges = selectedNode == null
        ? <GraphEdge>[]
        : viewModel.edgesForNode(selectedNode.id);

    return Container(
      width: 340,
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.95),
        border: Border(
          left: BorderSide(
            color: colorScheme.surfaceContainer.withOpacity(0.5),
          ),
        ),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 24),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Live Edit Panel',
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontSize: 18,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => viewModel.toggleEditPanel(),
                ),
              ],
            ),
            const SizedBox(height: 32),
            Text(
              'SELECTED ENTITY',
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w700,
                color: colorScheme.onSurfaceVariant,
                letterSpacing: 2,
              ),
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: colorScheme.primaryContainer.withOpacity(0.4),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: colorScheme.primary.withOpacity(0.1)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    selectedNode?.label ?? 'Nothing selected',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w700,
                      color: colorScheme.onPrimaryContainer,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    selectedNode == null
                        ? 'Tap a node to view relationships.'
                        : '${selectedNode.type.name.toUpperCase()} • ${selectedNode.documentCount} linked sections',
                    style: TextStyle(
                      fontSize: 12,
                      color: colorScheme.onPrimaryContainer.withOpacity(0.9),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'RELATIONSHIPS',
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w700,
                color: colorScheme.onSurfaceVariant,
                letterSpacing: 2,
              ),
            ),
            const SizedBox(height: 12),
            if (relatedEdges.isEmpty)
              Text(
                'Select a node to explore its triplets.',
                style: TextStyle(color: colorScheme.onSurfaceVariant),
              )
            else
              ...relatedEdges.map(
                (edge) => Container(
                  margin: const EdgeInsets.only(bottom: 8),
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: colorScheme.surfaceContainerLow,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: colorScheme.surfaceContainer),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              edge.relation,
                              style: const TextStyle(
                                fontWeight: FontWeight.w700,
                                fontSize: 13,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              edge.soHieu ?? 'N/A',
                              style: TextStyle(
                                color: colorScheme.onSurfaceVariant,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ),
                      IconButton(
                        onPressed: () => viewModel.selectNode(edge.to),
                        icon: const Icon(Icons.arrow_forward),
                        tooltip: 'Focus target node',
                      ),
                    ],
                  ),
                ),
              ),
            const Spacer(),
            SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                onPressed: viewModel.handleSaveChanges,
                icon: const Icon(Icons.save, size: 14),
                label: const Text('Save Changes'),
                style: FilledButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: viewModel.handleDeleteRelation,
                style: OutlinedButton.styleFrom(
                  foregroundColor: colorScheme.error,
                  side: BorderSide(color: colorScheme.error.withOpacity(0.2)),
                  backgroundColor: colorScheme.errorContainer.withOpacity(0.1),
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
                child: const Text('Delete Relation'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _GraphNodeChip extends StatelessWidget {
  const _GraphNodeChip({
    required this.node,
    required this.colorScheme,
    required this.selected,
  });

  final GraphNode node;
  final ColorScheme colorScheme;
  final bool selected;

  @override
  Widget build(BuildContext context) {
    final isSubject = node.type == GraphNodeType.subject;
    final baseColor = isSubject
        ? colorScheme.primary
        : colorScheme.tertiaryContainer;
    final foreground = isSubject
        ? colorScheme.onPrimaryContainer
        : colorScheme.onTertiaryContainer;

    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: baseColor.withOpacity(selected ? 1 : 0.85),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: selected ? colorScheme.primary : colorScheme.surfaceContainer,
          width: selected ? 2 : 1,
        ),
        boxShadow: [
          if (selected)
            BoxShadow(
              color: colorScheme.primary.withOpacity(0.25),
              blurRadius: 14,
              offset: const Offset(0, 6),
            ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            isSubject ? Icons.account_balance : Icons.gavel,
            size: 18,
            color: foreground,
          ),
          const SizedBox(width: 8),
          Text(
            node.label,
            style: TextStyle(
              color: foreground,
              fontWeight: FontWeight.w700,
              fontSize: 13,
            ),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.8),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                const Icon(Icons.link, size: 12),
                const SizedBox(width: 4),
                Text(
                  '${node.documentCount}',
                  style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
