import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../state/documents_view_model.dart';

class DocumentsView extends StatelessWidget {
  final DocumentsViewModel viewModel;

  const DocumentsView({super.key, required this.viewModel});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      backgroundColor: colorScheme.surface,
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _Header(viewModel: viewModel),
          _Filters(viewModel: viewModel),
          Expanded(child: _Content(viewModel: viewModel)),
        ],
      ),
    );
  }
}

class _Header extends StatelessWidget {
  final DocumentsViewModel viewModel;

  const _Header({required this.viewModel});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Padding(
      padding: const EdgeInsets.fromLTRB(40, 40, 40, 24),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      'VIETNAM LEGAL ARCHIVE',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        color: colorScheme.primary,
                        letterSpacing: 2,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      height: 4,
                      width: 32,
                      decoration: BoxDecoration(
                        color: colorScheme.tertiary,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'Legal Document Management',
                  style: theme.textTheme.headlineLarge?.copyWith(
                    fontSize: 36,
                    height: 1.2,
                  ),
                ),
              ],
            ),
          ),
          Row(
            children: [
              SizedBox(
                width: 256,
                child: TextField(
                  decoration: InputDecoration(
                    hintText: 'Search documents...',
                    hintStyle: TextStyle(
                      fontSize: 14,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                    prefixIcon: Icon(
                      Icons.search,
                      color: theme.colorScheme.onSurfaceVariant,
                      size: 20,
                    ),
                    filled: true,
                    fillColor: colorScheme.surfaceContainerLow,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                    contentPadding: const EdgeInsets.symmetric(vertical: 10),
                  ),
                  onChanged: viewModel.handleSearch,
                ),
              ),
              const SizedBox(width: 12),
              FilledButton.icon(
                onPressed: viewModel.handleAddDocument,
                icon: const Icon(Icons.upload_file, size: 20),
                label: const Text('Add Document'),
                style: FilledButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _Filters extends StatelessWidget {
  final DocumentsViewModel viewModel;

  const _Filters({required this.viewModel});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 16),
      child: Row(
        children: [
          Text(
            'FILTER BY TYPE:',
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w700,
              color: colorScheme.onSurfaceVariant,
              letterSpacing: 1.5,
            ),
          ),
          const SizedBox(width: 16),
          ...viewModel.filters.map(
            (filter) => Padding(
              padding: const EdgeInsets.only(right: 8),
              child: FilterChip(
                label: Text(filter),
                selected: viewModel.selectedFilter == filter,
                onSelected: (_) => viewModel.selectFilter(filter),
                backgroundColor: colorScheme.surfaceContainerHigh,
                selectedColor: colorScheme.secondary,
                labelStyle: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: viewModel.selectedFilter == filter
                      ? Colors.white
                      : colorScheme.onSurfaceVariant,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20),
                ),
              ),
            ),
          ),
          const Spacer(),
          TextButton.icon(
            onPressed: viewModel.handleAddDocument,
            icon: const Icon(Icons.filter_list, size: 16),
            label: const Text('Advanced'),
          ),
          const SizedBox(width: 16),
          TextButton.icon(
            onPressed: viewModel.handleAddDocument,
            icon: const Icon(Icons.sort, size: 16),
            label: const Text('Sort'),
          ),
        ],
      ),
    );
  }
}

class _Content extends StatelessWidget {
  final DocumentsViewModel viewModel;

  const _Content({required this.viewModel});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    final totalPages =
        (viewModel.totalDocuments == 0 ? 0 : (viewModel.totalDocuments / viewModel.documentsPerPage).ceil());

    return Padding(
      padding: const EdgeInsets.fromLTRB(40, 0, 40, 40),
      child: Container(
        decoration: BoxDecoration(
          color: colorScheme.surfaceContainerLow,
          borderRadius: BorderRadius.circular(32),
        ),
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Expanded(
              child: ListView.separated(
                itemBuilder: (context, index) {
                  final doc = viewModel.documents[index];
                  return _DocumentRow(
                    document: doc,
                    onTap: viewModel.handleDocumentTap,
                    onEdit: viewModel.handleEditDocument,
                    onDelete: viewModel.handleDeleteDocument,
                    onMore: viewModel.handleMoreOptions,
                  );
                },
                separatorBuilder: (_, __) => const SizedBox(height: 16),
                itemCount: viewModel.documents.length,
              ),
            ),
            _Pagination(
              viewModel: viewModel,
              totalPages: totalPages,
            ),
          ],
        ),
      ),
    );
  }
}

class _DocumentRow extends StatelessWidget {
  final DocumentItem document;
  final void Function(String id) onTap;
  final void Function(String id) onEdit;
  final void Function(String id) onDelete;
  final void Function(String id) onMore;

  const _DocumentRow({
    required this.document,
    required this.onTap,
    required this.onEdit,
    required this.onDelete,
    required this.onMore,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    final statusColor = _statusColor(document.statusTagColor, colorScheme);

    return InkWell(
      onTap: () => onTap(document.id),
      borderRadius: BorderRadius.circular(16),
      child: Container(
        decoration: BoxDecoration(
          color: colorScheme.surfaceContainerLowest,
          borderRadius: BorderRadius.circular(16),
        ),
        padding: const EdgeInsets.all(24),
        child: Row(
          children: [
            Expanded(
              flex: 3,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'ID: ${document.id}',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: colorScheme.primary,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    document.number,
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              flex: 6,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    document.title,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    document.field,
                    style: TextStyle(
                      fontSize: 11,
                      color: colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),
            Expanded(
              flex: 3,
              child: Text(
                document.date,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                  color: colorScheme.onSurfaceVariant,
                ),
              ),
            ),
            Expanded(
              flex: 3,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  document.status,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    color: statusColor,
                    letterSpacing: 0.5,
                  ),
                ),
              ),
            ),
            ConstrainedBox(
              constraints: const BoxConstraints(minWidth: 120),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  IconButton(
                    icon: const Icon(Icons.edit, size: 18),
                    color: colorScheme.primary,
                    onPressed: () => onEdit(document.id),
                    tooltip: 'Edit document',
                  ),
                  IconButton(
                    icon: const Icon(Icons.delete, size: 18),
                    color: colorScheme.error,
                    onPressed: () => onDelete(document.id),
                    tooltip: 'Delete document',
                  ),
                  IconButton(
                    icon: const Icon(Icons.more_vert, size: 18),
                    color: colorScheme.onSurfaceVariant,
                    onPressed: () => onMore(document.id),
                    tooltip: 'More options',
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _statusColor(String tag, ColorScheme colorScheme) {
    switch (tag) {
      case 'secondary':
        return colorScheme.secondary;
      case 'neutral':
        return colorScheme.onSurfaceVariant;
      default:
        return colorScheme.tertiary;
    }
  }
}

class _Pagination extends StatelessWidget {
  final DocumentsViewModel viewModel;
  final int totalPages;

  const _Pagination({
    required this.viewModel,
    required this.totalPages,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final start = ((viewModel.currentPage - 1) * viewModel.documentsPerPage + 1).clamp(1, viewModel.totalDocuments);
    final end = (viewModel.currentPage * viewModel.documentsPerPage).clamp(0, viewModel.totalDocuments);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      decoration: BoxDecoration(
        border: Border(
          top: BorderSide(
            color: colorScheme.outlineVariant.withOpacity(0.1),
          ),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          RichText(
            text: TextSpan(
              style: TextStyle(
                fontSize: 12,
                color: colorScheme.onSurfaceVariant,
              ),
              children: [
                const TextSpan(text: 'Showing '),
                TextSpan(
                  text: start.toString(),
                  style: TextStyle(
                    fontWeight: FontWeight.w700,
                    color: colorScheme.onSurface,
                  ),
                ),
                const TextSpan(text: '-'),
                TextSpan(
                  text: end.toString(),
                  style: TextStyle(
                    fontWeight: FontWeight.w700,
                    color: colorScheme.onSurface,
                  ),
                ),
                const TextSpan(text: ' of '),
                TextSpan(
                  text: viewModel.totalDocuments.toString(),
                  style: TextStyle(
                    fontWeight: FontWeight.w700,
                    color: colorScheme.onSurface,
                  ),
                ),
                const TextSpan(text: ' documents'),
              ],
            ),
          ),
          Row(
            children: [
              IconButton(
                icon: const Icon(Icons.chevron_left, size: 18),
                onPressed: viewModel.currentPage > 1
                    ? () => viewModel.changePage(viewModel.currentPage - 1)
                    : null,
              ),
              ..._pageButtons(totalPages, colorScheme),
              IconButton(
                icon: const Icon(Icons.chevron_right, size: 18),
                onPressed: viewModel.currentPage < totalPages
                    ? () => viewModel.changePage(viewModel.currentPage + 1)
                    : null,
              ),
            ],
          ),
        ],
      ),
    );
  }

  List<Widget> _pageButtons(int totalPages, ColorScheme colorScheme) {
    if (totalPages == 0) return const [];

    final pages = <Widget>[];
    final startPage = (viewModel.currentPage - 1).clamp(1, totalPages);
    final endPage = (viewModel.currentPage + 1).clamp(1, totalPages);

    for (var i = startPage; i <= endPage; i++) {
      pages.add(_PageButton(
        page: i,
        isSelected: i == viewModel.currentPage,
        onTap: () => viewModel.changePage(i),
        colorScheme: colorScheme,
      ));
    }

    return pages;
  }
}

class _PageButton extends StatelessWidget {
  final int page;
  final bool isSelected;
  final VoidCallback onTap;
  final ColorScheme colorScheme;

  const _PageButton({
    required this.page,
    required this.isSelected,
    required this.onTap,
    required this.colorScheme,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        width: 32,
        height: 32,
        margin: const EdgeInsets.symmetric(horizontal: 4),
        decoration: BoxDecoration(
          color: isSelected ? colorScheme.primary : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
        ),
        alignment: Alignment.center,
        child: Text(
          page.toString(),
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w700,
            color: isSelected ? Colors.white : colorScheme.onSurface,
          ),
        ),
      ),
    );
  }
}

class DocumentsScope extends StatelessWidget {
  final Widget child;

  const DocumentsScope({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => DocumentsViewModel(),
      child: child,
    );
  }
}
