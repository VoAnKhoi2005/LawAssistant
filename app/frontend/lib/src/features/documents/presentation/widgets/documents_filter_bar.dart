import 'package:flutter/material.dart';

class DocumentsFilterBar extends StatelessWidget {
  const DocumentsFilterBar({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 16),
      child: Row(
        children: [
          Text(
            'LỌC THEO LOẠI:',
            style: theme.textTheme.labelSmall?.copyWith(
              fontWeight: FontWeight.bold,
              letterSpacing: 1,
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Wrap(
              spacing: 8,
              children: [
                _FilterChip(label: 'Tất cả', isActive: true),
                const _FilterChip(label: 'Luật'),
                const _FilterChip(label: 'Nghị định'),
                const _FilterChip(label: 'Thông tư'),
                const _FilterChip(label: 'Quyết định'),
              ],
            ),
          ),
          IconButton.filledTonal(
            onPressed: () {},
            icon: const Icon(Icons.filter_list, size: 16),
            tooltip: 'Nâng cao',
          ),
          const SizedBox(width: 8),
          IconButton.filledTonal(
            onPressed: () {},
            icon: const Icon(Icons.sort, size: 16),
            tooltip: 'Sắp xếp',
          ),
        ],
      ),
    );
  }
}

class _FilterChip extends StatelessWidget {
  final String label;
  final bool isActive;

  const _FilterChip({
    required this.label,
    this.isActive = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return FilterChip(
      label: Text(
        label,
        style: theme.textTheme.labelSmall?.copyWith(
          fontWeight: FontWeight.bold,
          color: isActive
              ? theme.colorScheme.onSecondary
              : theme.colorScheme.onSurfaceVariant,
        ),
      ),
      selected: isActive,
      onSelected: (selected) {},
      selectedColor: theme.colorScheme.secondary,
      backgroundColor: theme.colorScheme.surfaceContainerHigh,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      labelPadding: EdgeInsets.zero,
    );
  }
}
