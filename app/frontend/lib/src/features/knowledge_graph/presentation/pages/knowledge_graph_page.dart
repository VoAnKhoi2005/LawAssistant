import 'package:flutter/material.dart';

/// Knowledge Graph Page - Graph visualization and editing interface
/// Follows clean architecture presentation layer pattern
class KnowledgeGraphPage extends StatefulWidget {
  const KnowledgeGraphPage({Key? key}) : super(key: key);

  @override
  State<KnowledgeGraphPage> createState() => _KnowledgeGraphPageState();
}

class _KnowledgeGraphPageState extends State<KnowledgeGraphPage> {
  String? _selectedDocument;
  String? _selectedSection;
  bool _showGraph = false;
  bool _showEditPanel = false;

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
                child: _showGraph
                    ? _buildGraphCanvas(theme, colorScheme)
                    : _buildEmptyState(theme, colorScheme),
              ),
            ],
          ),
          if (_showGraph && _showEditPanel)
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
                onPressed: _handleHistory,
                icon: const Icon(Icons.history, size: 16),
                label: const Text('History'),
                style: OutlinedButton.styleFrom(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  side: BorderSide(color: colorScheme.surfaceContainer),
                  backgroundColor: colorScheme.surfaceContainerHigh,
                ),
              ),
              const SizedBox(width: 12),
              IconButton(
                onPressed: _handleShare,
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
          _buildStep('1', 'Select Document', colorScheme,
              _selectedDocument ?? 'Select...', () => _handleSelectDocument()),
          Icon(Icons.arrow_forward,
              size: 14, color: colorScheme.outlineVariant.withOpacity(0.5)),
          const SizedBox(width: 16),
          _buildStep('2', 'Select Section', colorScheme,
              _selectedSection ?? 'Select...', () => _handleSelectSection()),
        ],
      ),
    );
  }

  Widget _buildStep(String number, String label, ColorScheme colorScheme,
      String value, VoidCallback onTap) {
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
            onPressed: () {
              setState(() {
                _showGraph = true;
                _selectedDocument = 'Bộ luật Dân sự 2015';
                _selectedSection = 'Điều 385';
              });
            },
            child: const Text('Show Example Graph'),
          ),
        ],
      ),
    );
  }

  Widget _buildStepIndicator(
      String number, String label, ColorScheme colorScheme) {
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

  Widget _buildGraphCanvas(ThemeData theme, ColorScheme colorScheme) {
    return Container(
      margin: const EdgeInsets.fromLTRB(32, 8, 32, 24),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: colorScheme.surfaceContainer),
      ),
      child: Stack(
        children: [
          Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.account_tree,
                  size: 64,
                  color: colorScheme.primary.withOpacity(0.3),
                ),
                const SizedBox(height: 16),
                Text(
                  'Graph Visualization Area',
                  style: theme.textTheme.titleLarge?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'TODO: Implement interactive graph visualization',
                  style: TextStyle(
                    fontSize: 14,
                    color: colorScheme.onSurfaceVariant.withOpacity(0.7),
                  ),
                ),
              ],
            ),
          ),
          _buildFloatingToolbar(colorScheme),
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
          _buildToolbarButton(Icons.zoom_in, colorScheme, _handleZoomIn),
          const SizedBox(height: 8),
          _buildToolbarButton(Icons.zoom_out, colorScheme, _handleZoomOut),
          const SizedBox(height: 8),
          _buildToolbarButton(
              Icons.center_focus_strong, colorScheme, _handleCenter),
          const SizedBox(height: 8),
          _buildToolbarButton(Icons.edit, colorScheme, () {
            setState(() => _showEditPanel = !_showEditPanel);
          }),
        ],
      ),
    );
  }

  Widget _buildToolbarButton(
      IconData icon, ColorScheme colorScheme, VoidCallback onTap) {
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

  Widget _buildEditSidebar(ThemeData theme, ColorScheme colorScheme) {
    return Container(
      width: 320,
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
                  onPressed: () {
                    setState(() => _showEditPanel = false);
                  },
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
              child: Text(
                'TODO: Display selected entity details',
                style: TextStyle(
                  fontSize: 12,
                  color: colorScheme.onPrimaryContainer,
                ),
              ),
            ),
            const Spacer(),
            Text(
              'TODO: Implement triplet editor, color picker, and action buttons',
              style: TextStyle(
                fontSize: 12,
                color: colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                onPressed: _handleSaveChanges,
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
                onPressed: _handleDeleteRelation,
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

  // TODO: Implement knowledge graph actions
  void _handleSelectDocument() {
    // TODO: Show document selection dialog
    debugPrint('TODO: Show document selection dialog');
  }

  void _handleSelectSection() {
    // TODO: Show section selection dialog
    debugPrint('TODO: Show section selection dialog');
  }

  void _handleHistory() {
    // TODO: Show graph history
    debugPrint('TODO: Show graph history');
  }

  void _handleShare() {
    // TODO: Implement share functionality
    debugPrint('TODO: Share graph');
  }

  void _handleZoomIn() {
    // TODO: Implement zoom in
    debugPrint('TODO: Zoom in');
  }

  void _handleZoomOut() {
    // TODO: Implement zoom out
    debugPrint('TODO: Zoom out');
  }

  void _handleCenter() {
    // TODO: Center graph view
    debugPrint('TODO: Center graph');
  }

  void _handleSaveChanges() {
    // TODO: Save entity/relation changes
    debugPrint('TODO: Save changes');
  }

  void _handleDeleteRelation() {
    // TODO: Delete selected relation
    debugPrint('TODO: Delete relation');
  }
}
