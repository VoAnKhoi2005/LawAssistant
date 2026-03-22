import 'package:flutter/material.dart';

/// Sections Page - Legal sections explorer interface
/// Follows clean architecture presentation layer pattern
class SectionsPage extends StatefulWidget {
  const SectionsPage({Key? key}) : super(key: key);

  @override
  State<SectionsPage> createState() => _SectionsPageState();
}

class _SectionsPageState extends State<SectionsPage> {
  String _selectedDocument = 'Luật Đất đai 2024';
  bool _showIncomingRelations = true;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      backgroundColor: colorScheme.surface,
      body: Row(
        children: [
          _buildSidePanel(theme, colorScheme),
          Expanded(child: _buildMainContent(theme, colorScheme)),
        ],
      ),
    );
  }

  Widget _buildSidePanel(ThemeData theme, ColorScheme colorScheme) {
    return Container(
      width: 350,
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
                _buildDocumentSelector(theme, colorScheme),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32),
            child: _buildSearchField(theme, colorScheme),
          ),
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32),
            child: _buildFilters(theme, colorScheme),
          ),
          const SizedBox(height: 24),
          Expanded(child: _buildHierarchyTree(theme, colorScheme)),
        ],
      ),
    );
  }

  Widget _buildDocumentSelector(ThemeData theme, ColorScheme colorScheme) {
    return DropdownMenu<String>(
      initialSelection: _selectedDocument,
      textStyle: theme.textTheme.bodyMedium?.copyWith(
        color: colorScheme.primary,
        fontWeight: FontWeight.w600,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: colorScheme.surfaceContainerLow,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 10,
        ),
      ),
      onSelected: (value) {
        if (value != null) {
          setState(() => _selectedDocument = value);
        }
      },
      dropdownMenuEntries: const [
        DropdownMenuEntry(
          value: 'Luật Đất đai 2024',
          label: 'Luật Đất đai 2024',
        ),
        DropdownMenuEntry(value: 'Luật Xây dựng', label: 'Luật Xây dựng'),
      ],
    );
  }

  Widget _buildBadge(String text, ColorScheme colorScheme) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      decoration: BoxDecoration(
        color: colorScheme.tertiaryContainer.withOpacity(0.2),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w700,
          color: colorScheme.tertiary,
          letterSpacing: 1,
        ),
      ),
    );
  }

  Widget _buildSearchField(ThemeData theme, ColorScheme colorScheme) {
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
      onChanged: (value) {
        // TODO: Implement search functionality
        debugPrint('TODO: Search for: $value');
      },
    );
  }

  Widget _buildFilters(ThemeData theme, ColorScheme colorScheme) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        _buildFilterChip('All', true, theme, colorScheme),
        _buildFilterChip(
          'Amendments',
          false,
          theme,
          colorScheme,
          icon: Icons.edit_note,
        ),
        _buildFilterChip(
          'Appendix',
          false,
          theme,
          colorScheme,
          icon: Icons.attachment,
        ),
      ],
    );
  }

  Widget _buildFilterChip(
    String label,
    bool selected,
    ThemeData theme,
    ColorScheme colorScheme, {
    IconData? icon,
  }) {
    return InkWell(
      onTap: () {
        // TODO: Handle filter selection
        debugPrint('TODO: Filter by: $label');
      },
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: selected
              ? colorScheme.primary
              : colorScheme.surfaceContainerHigh,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (icon != null) ...[
              Icon(
                icon,
                size: 14,
                color: selected ? Colors.white : colorScheme.onSurfaceVariant,
              ),
              const SizedBox(width: 4),
            ],
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: selected ? Colors.white : colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHierarchyTree(ThemeData theme, ColorScheme colorScheme) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 24),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerLow,
        borderRadius: BorderRadius.circular(24),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'DOCUMENT STRUCTURE',
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w800,
              color: colorScheme.outlineVariant,
              letterSpacing: 2,
            ),
          ),
          const SizedBox(height: 24),
          Expanded(
            child: ListView(
              children: [
                _buildTreeNode(
                  'Chương I',
                  'Quy định chung',
                  true,
                  theme,
                  colorScheme,
                  onTap: () => _handleNodeTap('chuong-1'),
                  children: [
                    _buildTreeNode(
                      'Mục 1',
                      'Phạm vi điều chỉnh',
                      true,
                      theme,
                      colorScheme,
                      level: 1,
                      onTap: () => _handleNodeTap('muc-1'),
                      children: [
                        _buildTreeNode(
                          'Điều 1',
                          '',
                          false,
                          theme,
                          colorScheme,
                          level: 2,
                          isSelected: true,
                          onTap: () => _handleNodeTap('dieu-1'),
                          children: [
                            _buildSubItem(
                              'Khoản 1',
                              theme,
                              colorScheme,
                              onTap: () => _handleNodeTap('khoan-1'),
                            ),
                            _buildSubItem(
                              'Khoản 2',
                              theme,
                              colorScheme,
                              onTap: () => _handleNodeTap('khoan-2'),
                            ),
                            _buildSubItem(
                              'Điểm a',
                              theme,
                              colorScheme,
                              isItalic: true,
                              level: 1,
                              onTap: () => _handleNodeTap('diem-a'),
                            ),
                          ],
                        ),
                        _buildTreeNode(
                          'Điều 2',
                          '',
                          false,
                          theme,
                          colorScheme,
                          level: 2,
                          onTap: () => _handleNodeTap('dieu-2'),
                        ),
                      ],
                    ),
                  ],
                ),
                _buildTreeNode(
                  'Chương II',
                  'Quyền và nghĩa vụ',
                  false,
                  theme,
                  colorScheme,
                  opacity: 0.6,
                  onTap: () => _handleNodeTap('chuong-2'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTreeNode(
    String title,
    String subtitle,
    bool expanded,
    ThemeData theme,
    ColorScheme colorScheme, {
    int level = 0,
    bool isSelected = false,
    double opacity = 1.0,
    List<Widget>? children,
    VoidCallback? onTap,
  }) {
    return Opacity(
      opacity: opacity,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          InkWell(
            onTap: onTap,
            borderRadius: BorderRadius.circular(8),
            child: Container(
              padding: const EdgeInsets.all(8),
              margin: EdgeInsets.only(left: level * 24.0),
              decoration: BoxDecoration(
                color: isSelected
                    ? colorScheme.secondaryContainer
                    : Colors.transparent,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(
                    expanded
                        ? Icons.keyboard_arrow_down
                        : Icons.keyboard_arrow_right,
                    size: level == 2 ? 18 : 20,
                    color: isSelected
                        ? colorScheme.onSecondaryContainer
                        : colorScheme.outline,
                  ),
                  const SizedBox(width: 8),
                  if (isSelected)
                    Icon(
                      Icons.radio_button_checked,
                      size: 18,
                      color: colorScheme.onSecondaryContainer,
                    ),
                  if (isSelected) const SizedBox(width: 8),
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: level == 0
                          ? FontWeight.w700
                          : FontWeight.w600,
                      color: isSelected
                          ? colorScheme.onSecondaryContainer
                          : colorScheme.onSurface,
                    ),
                  ),
                  if (subtitle.isNotEmpty) ...[
                    const SizedBox(width: 8),
                    Text(
                      subtitle,
                      style: TextStyle(
                        fontSize: 10,
                        fontStyle: FontStyle.italic,
                        color: colorScheme.outlineVariant,
                      ),
                    ),
                  ],
                  if (isSelected) ...[
                    const Spacer(),
                    Icon(
                      Icons.chevron_right,
                      size: 16,
                      color: colorScheme.onSecondaryContainer,
                    ),
                  ],
                ],
              ),
            ),
          ),
          if (children != null && expanded) ...children,
        ],
      ),
    );
  }

  Widget _buildSubItem(
    String label,
    ThemeData theme,
    ColorScheme colorScheme, {
    bool isItalic = false,
    int level = 0,
    VoidCallback? onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(8),
        margin: EdgeInsets.only(left: 64.0 + (level * 16)),
        child: Row(
          children: [
            Container(
              width: 6,
              height: 6,
              decoration: BoxDecoration(
                color: colorScheme.outlineVariant.withOpacity(
                  level == 0 ? 0.4 : 0.2,
                ),
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 8),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                fontStyle: isItalic ? FontStyle.italic : FontStyle.normal,
                color: colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMainContent(ThemeData theme, ColorScheme colorScheme) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildArticleContent(theme, colorScheme),
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

  Widget _buildArticleContent(ThemeData theme, ColorScheme colorScheme) {
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
              _buildStatusBadge(
                'Status: Effective',
                colorScheme.primary,
                colorScheme,
              ),
              const SizedBox(width: 12),
              _buildStatusBadge(
                'Revised: 2023',
                colorScheme.onSurfaceVariant,
                colorScheme,
              ),
              const Spacer(),
              Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.print),
                    onPressed: _handlePrint,
                    color: colorScheme.outline,
                    tooltip: 'Print',
                  ),
                  IconButton(
                    icon: const Icon(Icons.share),
                    onPressed: _handleShare,
                    color: colorScheme.outline,
                    tooltip: 'Share',
                  ),
                  IconButton(
                    icon: const Icon(Icons.history),
                    onPressed: _handleHistory,
                    color: colorScheme.outline,
                    tooltip: 'View history',
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            'Điều 1. Phạm vi điều chỉnh',
            style: theme.textTheme.headlineLarge?.copyWith(
              fontSize: 30,
              height: 1.3,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Ref: 01/2024/L-CTN • Type: General Provisions',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: colorScheme.outlineVariant,
            ),
          ),
          const SizedBox(height: 32),
          Text(
            'Luật này quy định về chế độ sở hữu đất đai, quyền hạn và trách nhiệm của Nhà nước đại diện chủ sở hữu toàn dân về đất đai và thống nhất quản lý về đất đai, chế độ quản lý và sử dụng đất đai, quyền và nghĩa vụ của công dân, người sử dụng đất đối với đất đai thuộc lãnh thổ của nước Cộng hòa xã hội chủ nghĩa Việt Nam.',
            style: theme.textTheme.bodyLarge?.copyWith(
              height: 1.6,
              color: colorScheme.onSurface,
            ),
          ),
          const SizedBox(height: 24),
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              border: Border(
                left: BorderSide(color: colorScheme.primaryContainer, width: 2),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '1. Đất đai thuộc sở hữu toàn dân do Nhà nước đại diện chủ sở hữu và thống nhất quản lý.',
                  style: TextStyle(
                    fontSize: 14,
                    fontStyle: FontStyle.italic,
                    color: colorScheme.onSurfaceVariant,
                    height: 1.6,
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  '2. Nhà nước trao quyền sử dụng đất cho người sử dụng đất theo quy định của Luật này.',
                  style: TextStyle(
                    fontSize: 14,
                    fontStyle: FontStyle.italic,
                    color: colorScheme.onSurfaceVariant,
                    height: 1.6,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusBadge(String text, Color color, ColorScheme colorScheme) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color == colorScheme.primary
            ? color.withOpacity(0.1)
            : colorScheme.surfaceContainer,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w700,
          color: color,
          letterSpacing: 1,
        ),
      ),
    );
  }

  // TODO: Implement section actions
  void _handleDocumentSelection() {
    // TODO: Show document selection dialog
    debugPrint('TODO: Show document selection dialog');
  }

  void _handleNodeTap(String nodeId) {
    // TODO: Load and display section content
    debugPrint('TODO: Load section content for: $nodeId');
  }

  void _handlePrint() {
    // TODO: Implement print functionality
    debugPrint('TODO: Print current section');
  }

  void _handleShare() {
    // TODO: Implement share functionality
    debugPrint('TODO: Share current section');
  }

  void _handleHistory() {
    // TODO: Show section history
    debugPrint('TODO: Show section history');
  }
}
