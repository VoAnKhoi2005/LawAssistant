import 'package:flutter/material.dart';

import '../../domain/models/section_content.dart';
import '../state/sections_view_model.dart';
import 'hierarchy_tree_widget.dart';

class SectionsView extends StatelessWidget {
  final SectionsViewModel viewModel;

  const SectionsView({super.key, required this.viewModel});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      backgroundColor: colorScheme.surface,
      body: Row(
        children: [
          _SidePanel(viewModel: viewModel),
          Expanded(child: _MainContent(viewModel: viewModel)),
        ],
      ),
    );
  }
}

class _SidePanel extends StatelessWidget {
  final SectionsViewModel viewModel;

  const _SidePanel({required this.viewModel});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Container(
      width: 400,
      color: colorScheme.surfaceContainerLow,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Section Management',
                  style: theme.textTheme.headlineLarge?.copyWith(fontSize: 36),
                ),
                const SizedBox(height: 16),
                _DocumentSelector(viewModel: viewModel),
                const SizedBox(height: 8),
                Chip(
                  label: const Text('HIERARCHY SYSTEM'),
                  labelStyle: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    color: colorScheme.tertiary,
                    letterSpacing: 1,
                  ),
                  backgroundColor: colorScheme.tertiaryContainer.withOpacity(
                    0.2,
                  ),
                  side: BorderSide.none,
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32),
            child: _SearchField(viewModel: viewModel),
          ),
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32),
            child: _Filters(viewModel: viewModel),
          ),
          const SizedBox(height: 24),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(0, 0, 0, 20),
              child: HierarchyTreeWidget(
                nodes: viewModel.hierarchyNodes,
                selectedNodeId: viewModel.selectedNodeId,
                onNodeSelected: viewModel.selectNode,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _DocumentSelector extends StatelessWidget {
  final SectionsViewModel viewModel;

  const _DocumentSelector({required this.viewModel});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return DropdownButtonFormField<String>(
      value: viewModel.selectedDocument,
      decoration: InputDecoration(
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 10,
        ),
        filled: true,
        fillColor: colorScheme.surfaceContainer,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: colorScheme.outline.withOpacity(0.2)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: colorScheme.outline.withOpacity(0.2)),
        ),
      ),
      icon: Icon(Icons.expand_more, color: colorScheme.outline, size: 16),
      style: TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: colorScheme.primary,
      ),
      dropdownColor: colorScheme.surface,
      items: viewModel.availableDocuments
          .map((doc) => DropdownMenuItem(value: doc, child: Text(doc)))
          .toList(),
      onChanged: viewModel.selectDocument,
    );
  }
}

class _SearchField extends StatelessWidget {
  final SectionsViewModel viewModel;

  const _SearchField({required this.viewModel});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return TextField(
      decoration: InputDecoration(
        hintText: 'Search sections, codes, or keywords...',
        hintStyle: TextStyle(fontSize: 14, color: colorScheme.outlineVariant),
        prefixIcon: Icon(Icons.search, color: colorScheme.outline, size: 20),
        filled: true,
        fillColor: colorScheme.surfaceContainer,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide.none,
        ),
        contentPadding: const EdgeInsets.symmetric(vertical: 16),
      ),
      onChanged: viewModel.search,
    );
  }
}

class _Filters extends StatelessWidget {
  final SectionsViewModel viewModel;

  const _Filters({required this.viewModel});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: viewModel.filters.map((filter) {
        final label = filter['label'] as String;
        final icon = filter['icon'] as IconData?;
        final isSelected = viewModel.selectedFilter == label;

        return FilterChip(
          label: Text(label),
          avatar: icon != null ? Icon(icon, size: 14) : null,
          selected: isSelected,
          onSelected: (_) => viewModel.selectFilter(label),
          backgroundColor: colorScheme.surfaceContainerHigh,
          selectedColor: colorScheme.primary,
          labelStyle: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w700,
            color: isSelected ? Colors.white : colorScheme.onSurfaceVariant,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
        );
      }).toList(),
    );
  }
}

class _MainContent extends StatelessWidget {
  final SectionsViewModel viewModel;

  const _MainContent({required this.viewModel});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    final content = viewModel.currentContent;
    if (content == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.description_outlined,
              size: 64,
              color: colorScheme.outlineVariant,
            ),
            const SizedBox(height: 16),
            Text(
              'Select a section from the tree',
              style: theme.textTheme.titleMedium?.copyWith(
                color: colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _ArticleContent(
            content: content,
            onPrint: viewModel.handlePrint,
            onShare: viewModel.handleShare,
            onHistory: viewModel.handleHistory,
          ),
          const SizedBox(height: 64),
          Text(
            'Document Relations',
            style: theme.textTheme.headlineLarge?.copyWith(fontSize: 24),
          ),
          const SizedBox(height: 16),
          Text(
            'TODO: Implement document relations display',
            style: TextStyle(color: colorScheme.onSurfaceVariant),
          ),
        ],
      ),
    );
  }
}

class _ArticleContent extends StatelessWidget {
  final SectionContent content;
  final VoidCallback onPrint;
  final VoidCallback onShare;
  final VoidCallback onHistory;

  const _ArticleContent({
    required this.content,
    required this.onPrint,
    required this.onShare,
    required this.onHistory,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Container(
      padding: const EdgeInsets.all(40),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(32),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF525F71).withOpacity(0.1),
            blurRadius: 80,
            offset: const Offset(0, 40),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Chip(
                label: Text(content.status.displayName),
                labelStyle: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w700,
                  color: colorScheme.primary,
                  letterSpacing: 1,
                ),
                backgroundColor: colorScheme.primary.withOpacity(0.1),
                side: BorderSide.none,
              ),
              if (content.revisionDate != null) ...[
                const SizedBox(width: 12),
                Chip(
                  label: Text('Revised: ${content.revisionDate}'),
                  labelStyle: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    color: colorScheme.onSurfaceVariant,
                    letterSpacing: 1,
                  ),
                  backgroundColor: colorScheme.surfaceContainer,
                  side: BorderSide.none,
                ),
              ],
              const Spacer(),
              Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.print),
                    onPressed: onPrint,
                    color: colorScheme.outline,
                    tooltip: 'Print',
                  ),
                  IconButton(
                    icon: const Icon(Icons.share),
                    onPressed: onShare,
                    color: colorScheme.outline,
                    tooltip: 'Share',
                  ),
                  IconButton(
                    icon: const Icon(Icons.history),
                    onPressed: onHistory,
                    color: colorScheme.outline,
                    tooltip: 'View history',
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            content.title,
            style: theme.textTheme.headlineLarge?.copyWith(
              fontSize: 30,
              height: 1.3,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Ref: ${content.reference} • Type: ${content.type}',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: colorScheme.outlineVariant,
            ),
          ),
          const SizedBox(height: 32),
          Text(
            content.content,
            style: theme.textTheme.bodyLarge?.copyWith(
              height: 1.6,
              color: colorScheme.onSurface,
            ),
          ),
          if (content.paragraphs.isNotEmpty) ...[
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                border: Border(
                  left: BorderSide(
                    color: colorScheme.primaryContainer,
                    width: 2,
                  ),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: content.paragraphs.asMap().entries.map((entry) {
                  final index = entry.key;
                  final paragraph = entry.value;
                  return Padding(
                    padding: EdgeInsets.only(
                      bottom: index < content.paragraphs.length - 1 ? 16 : 0,
                    ),
                    child: Text(
                      '${index + 1}. $paragraph',
                      style: TextStyle(
                        fontSize: 14,
                        fontStyle: FontStyle.italic,
                        color: colorScheme.onSurfaceVariant,
                        height: 1.6,
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),
          ],
          if (content.metadata != null) ...[
            const SizedBox(height: 48),
            _Metadata(metadata: content.metadata!),
          ],
        ],
      ),
    );
  }
}

class _Metadata extends StatelessWidget {
  final SectionMetadata metadata;

  const _Metadata({required this.metadata});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.only(top: 48),
      decoration: BoxDecoration(
        border: Border(
          top: BorderSide(color: colorScheme.outlineVariant.withOpacity(0.1)),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (metadata.originalSource != null)
            Expanded(
              child: _MetadataItem(
                label: 'ORIGINAL SOURCE',
                value: metadata.originalSource!,
                isLink: true,
              ),
            ),
          if (metadata.authorizingBody != null)
            Expanded(
              child: _MetadataItem(
                label: 'AUTHORIZING BODY',
                value: metadata.authorizingBody!,
              ),
            ),
          if (metadata.tags.isNotEmpty)
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'CATEGORY TAGS',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w800,
                      color: colorScheme.outlineVariant,
                      letterSpacing: 2,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: metadata.tags
                        .map(
                          (tag) => Chip(
                            label: Text(tag),
                            labelStyle: TextStyle(
                              fontSize: 10,
                              color: colorScheme.onSurfaceVariant,
                            ),
                            backgroundColor:
                                colorScheme.surfaceContainerHighest,
                            side: BorderSide.none,
                            padding: EdgeInsets.zero,
                          ),
                        )
                        .toList(),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

class _MetadataItem extends StatelessWidget {
  final String label;
  final String value;
  final bool isLink;

  const _MetadataItem({
    required this.label,
    required this.value,
    this.isLink = false,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w800,
            color: colorScheme.outlineVariant,
            letterSpacing: 2,
          ),
        ),
        const SizedBox(height: 8),
        InkWell(
          onTap: isLink ? () => debugPrint('TODO: Open source: $value') : null,
          child: Text(
            value,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: isLink ? colorScheme.primary : colorScheme.onSurface,
              decoration: isLink ? TextDecoration.underline : null,
              decorationColor: colorScheme.primary.withOpacity(0.3),
            ),
          ),
        ),
      ],
    );
  }
}
