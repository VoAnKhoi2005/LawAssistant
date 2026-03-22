import 'dart:math' as math;

import 'package:flutter/material.dart';

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
                  style: theme.textTheme.headlineLarge?.copyWith(
                    fontSize: 30,
                  ),
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
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
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
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 4,
          ),
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
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
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

  Widget _buildStepIndicator(String number, String label, ColorScheme colorScheme) {
    return Column(
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            border: Border.all(
              color: colorScheme.outlineVariant,
            ),
            shape: BoxShape.circle,
          ),
          alignment: Alignment.center,
          child: Text(
            number,
            style: TextStyle(
              fontSize: 12,
              color: colorScheme.outlineVariant,
            ),
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
    return Container(
      margin: const EdgeInsets.fromLTRB(32, 8, 32, 24),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: colorScheme.surfaceContainer),
      ),
      child: Stack(
        children: [
          TripletGraphCanvas(
            nodes: viewModel.graphNodes,
            edges: viewModel.graphEdges,
            onNodeSelected: viewModel.selectNode,
            selectedNodeId: viewModel.selectedNodeId,
          ),
          _buildFloatingToolbar(colorScheme),
          Positioned(
            right: 24,
            top: 24,
            child: _buildLegend(colorScheme),
          ),
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
          _buildToolbarButton(Icons.zoom_in, colorScheme, viewModel.handleZoomIn),
          const SizedBox(height: 8),
          _buildToolbarButton(Icons.zoom_out, colorScheme, viewModel.handleZoomOut),
          const SizedBox(height: 8),
          _buildToolbarButton(Icons.center_focus_strong, colorScheme, viewModel.handleCenter),
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
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 8,
            ),
          ],
        ),
        child: Icon(
          icon,
          size: 20,
          color: colorScheme.primary,
        ),
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
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
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
            legendItem(colorScheme.primaryContainer, 'Subject', Icons.account_balance),
            const SizedBox(width: 12),
            legendItem(colorScheme.tertiaryContainer, 'Object', Icons.gavel),
          ],
        ),
      ),
    );
  }

  Widget _buildEditSidebar(ThemeData theme, ColorScheme colorScheme) {
    final selectedNode = viewModel.selectedNode;
    final relatedEdges =
        selectedNode == null ? <GraphEdge>[] : viewModel.edgesForNode(selectedNode.id);

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
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 24,
          ),
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
                border: Border.all(
                  color: colorScheme.primary.withOpacity(0.1),
                ),
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

class TripletGraphCanvas extends StatelessWidget {
  const TripletGraphCanvas({
    super.key,
    required this.nodes,
    required this.edges,
    required this.onNodeSelected,
    required this.selectedNodeId,
  });

  final List<GraphNode> nodes;
  final List<GraphEdge> edges;
  final ValueChanged<String?> onNodeSelected;
  final String? selectedNodeId;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return LayoutBuilder(
      builder: (context, constraints) {
        final size = constraints.biggest;
        final positions = _calculateNodePositions(size, nodes);
        final nodeRadius = 28.0;

        return Stack(
          children: [
            CustomPaint(
              size: size,
              painter: TripletGraphPainter(
                positions: positions,
                edges: edges,
                colorScheme: colorScheme,
              ),
            ),
            ...nodes.map((node) {
              final position = positions[node.id] ?? Offset.zero;
              final selected = node.id == selectedNodeId;
              return Positioned(
                left: position.dx - nodeRadius,
                top: position.dy - nodeRadius,
                child: GestureDetector(
                  onTap: () => onNodeSelected(node.id),
                  child: _GraphNodeChip(
                    node: node,
                    colorScheme: colorScheme,
                    selected: selected,
                  ),
                ),
              );
            }),
          ],
        );
      },
    );
  }

  Map<String, Offset> _calculateNodePositions(Size size, List<GraphNode> nodes) {
    final subjects = nodes.where((n) => n.type == GraphNodeType.subject).toList();
    final objects = nodes.where((n) => n.type == GraphNodeType.object).toList();

    double slotY(int index, int count) {
      const topPadding = 60.0;
      const bottomPadding = 60.0;
      final available = size.height - topPadding - bottomPadding;
      if (available <= 0) return topPadding;
      return topPadding + available * (index + 1) / (count + 1);
    }

    final positions = <String, Offset>{};
    for (var i = 0; i < subjects.length; i++) {
      positions[subjects[i].id] = Offset(size.width * 0.22, slotY(i, subjects.length));
    }
    for (var i = 0; i < objects.length; i++) {
      positions[objects[i].id] = Offset(size.width * 0.78, slotY(i, objects.length));
    }

    // Fallback to spread in center if a side is empty
    if (subjects.isEmpty && objects.isNotEmpty) {
      for (var i = 0; i < objects.length; i++) {
        positions[objects[i].id] = Offset(size.width * 0.5, slotY(i, objects.length));
      }
    }
    if (objects.isEmpty && subjects.isNotEmpty) {
      for (var i = 0; i < subjects.length; i++) {
        positions[subjects[i].id] = Offset(size.width * 0.5, slotY(i, subjects.length));
      }
    }

    return positions;
  }
}

class TripletGraphPainter extends CustomPainter {
  TripletGraphPainter({
    required this.positions,
    required this.edges,
    required this.colorScheme,
  });

  final Map<String, Offset> positions;
  final List<GraphEdge> edges;
  final ColorScheme colorScheme;

  @override
  void paint(Canvas canvas, Size size) {
    final edgePaint = Paint()
      ..color = colorScheme.outlineVariant
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    for (final edge in edges) {
      final start = positions[edge.from];
      final end = positions[edge.to];
      if (start == null || end == null) continue;

      final path = Path()
        ..moveTo(start.dx, start.dy)
        ..lineTo(end.dx, end.dy);
      canvas.drawPath(path, edgePaint);

      _drawArrow(canvas, start, end, colorScheme.outlineVariant);
      _drawLabel(canvas, start, end, edge.relation);
    }
  }

  void _drawArrow(Canvas canvas, Offset start, Offset end, Color color) {
    const arrowSize = 8.0;
    final direction = (end - start);
    final angle = math.atan2(direction.dy, direction.dx);
    final arrowP1 = end - Offset(math.cos(angle - math.pi / 6), math.sin(angle - math.pi / 6)) * arrowSize;
    final arrowP2 = end - Offset(math.cos(angle + math.pi / 6), math.sin(angle + math.pi / 6)) * arrowSize;

    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.fill;
    final path = Path()
      ..moveTo(end.dx, end.dy)
      ..lineTo(arrowP1.dx, arrowP1.dy)
      ..lineTo(arrowP2.dx, arrowP2.dy)
      ..close();
    canvas.drawPath(path, paint);
  }

  void _drawLabel(Canvas canvas, Offset start, Offset end, String label) {
    final midpoint = Offset((start.dx + end.dx) / 2, (start.dy + end.dy) / 2);
    final textSpan = TextSpan(
      text: label,
      style: TextStyle(
        color: colorScheme.onSurfaceVariant,
        fontSize: 11,
        fontWeight: FontWeight.w600,
      ),
    );
    final tp = TextPainter(
      text: textSpan,
      textAlign: TextAlign.center,
      textDirection: TextDirection.ltr,
    )..layout(minWidth: 0, maxWidth: 180);
    final offset = midpoint - Offset(tp.width / 2, tp.height / 2);
    tp.paint(canvas, offset);
  }

  @override
  bool shouldRepaint(covariant TripletGraphPainter oldDelegate) {
    return oldDelegate.positions != positions || oldDelegate.edges != edges;
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
    final baseColor = isSubject ? colorScheme.primaryContainer : colorScheme.tertiaryContainer;
    final foreground = isSubject ? colorScheme.onPrimaryContainer : colorScheme.onTertiaryContainer;

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
                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
