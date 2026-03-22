import 'package:flutter/material.dart';

import '../../domain/models/section_content.dart';
import '../../domain/models/section_node.dart';
import '../widgets/hierarchy_tree_widget.dart';

/// Sections Page - Legal sections explorer interface
/// Follows clean architecture presentation layer pattern
class SectionsPage extends StatefulWidget {
  const SectionsPage({Key? key}) : super(key: key);

  @override
  State<SectionsPage> createState() => _SectionsPageState();
}

class _SectionsPageState extends State<SectionsPage> {
  String? _selectedDocument;
  String? _selectedNodeId;
  List<SectionNode> _hierarchyNodes = [];
  SectionContent? _currentContent;
  String _selectedFilter = 'All';

  @override
  void initState() {
    super.initState();
    _loadMockData();
  }

  void _loadMockData() {
    // TODO: Replace with actual API call
    _hierarchyNodes = [
      SectionNode(
        id: 'chuong-1',
        title: 'Chương I',
        subtitle: 'Quy định chung',
        type: SectionNodeType.chapter,
        children: [
          SectionNode(
            id: 'muc-1',
            title: 'Mục 1',
            subtitle: 'Phạm vi điều chỉnh',
            type: SectionNodeType.section,
            children: [
              SectionNode(
                id: 'dieu-1',
                title: 'Điều 1',
                type: SectionNodeType.article,
                children: [
                  SectionNode(
                    id: 'khoan-1',
                    title: 'Khoản 1',
                    type: SectionNodeType.clause,
                  ),
                  SectionNode(
                    id: 'khoan-2',
                    title: 'Khoản 2',
                    type: SectionNodeType.clause,
                    children: [
                      SectionNode(
                        id: 'diem-a',
                        title: 'Điểm a',
                        type: SectionNodeType.point,
                      ),
                    ],
                  ),
                ],
              ),
              SectionNode(
                id: 'dieu-2',
                title: 'Điều 2',
                type: SectionNodeType.article,
              ),
            ],
          ),
        ],
      ),
      SectionNode(
        id: 'chuong-2',
        title: 'Chương II',
        subtitle: 'Quyền và nghĩa vụ',
        type: SectionNodeType.chapter,
      ),
    ];

    _selectedDocument = 'Luật Đất đai 2024';
    _selectedNodeId = 'dieu-1';
    _currentContent = SectionContent(
      id: 'dieu-1',
      title: 'Điều 1. Phạm vi điều chỉnh',
      reference: '01/2024/L-CTN',
      type: 'General Provisions',
      content:
          'Luật này quy định về chế độ sở hữu đất đai, quyền hạn và trách nhiệm của Nhà nước đại diện chủ sở hữu toàn dân về đất đai và thống nhất quản lý về đất đai, chế độ quản lý và sử dụng đất đai, quyền và nghĩa vụ của công dân, người sử dụng đất đối với đất đai thuộc lãnh thổ của nước Cộng hòa xã hội chủ nghĩa Việt Nam.',
      paragraphs: [
        'Đất đai thuộc sở hữu toàn dân do Nhà nước đại diện chủ sở hữu và thống nhất quản lý.',
        'Nhà nước trao quyền sử dụng đất cho người sử dụng đất theo quy định của Luật này.',
      ],
      status: SectionStatus.effective,
      revisionDate: '2023',
      metadata: SectionMetadata(
        originalSource: 'Văn bản hợp nhất số 12/VBHN-VPQH',
        authorizingBody: 'Quốc hội Khóa XV',
        tags: ['Real Estate', 'Civil'],
      ),
    );
  }

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
                _buildDocumentSelector(theme, colorScheme),
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
            child: _buildSearchField(theme, colorScheme),
          ),
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32),
            child: _buildFilters(theme, colorScheme),
          ),
          const SizedBox(height: 24),
          Expanded(
            child: HierarchyTreeWidget(
              nodes: _hierarchyNodes,
              selectedNodeId: _selectedNodeId,
              onNodeSelected: _handleNodeSelected,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDocumentSelector(ThemeData theme, ColorScheme colorScheme) {
    return DropdownButtonFormField<String>(
      value: _selectedDocument,
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
      items: const [
        DropdownMenuItem(
          value: 'Luật Đất đai 2024',
          child: Text('Luật Đất đai 2024'),
        ),
        DropdownMenuItem(
          value: 'Bộ luật Dân sự 2015',
          child: Text('Bộ luật Dân sự 2015'),
        ),
        DropdownMenuItem(
          value: 'Luật Đầu tư 2020',
          child: Text('Luật Đầu tư 2020'),
        ),
      ],
      onChanged: (value) {
        if (value == null) return;
        setState(() => _selectedDocument = value);
        _handleDocumentChanged(value);
      },
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
    final filters = [
      {'label': 'All', 'icon': null},
      {'label': 'Amendments', 'icon': Icons.edit_note},
      {'label': 'Appendix', 'icon': Icons.attachment},
    ];

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: filters.map((filter) {
        final label = filter['label'] as String;
        final icon = filter['icon'] as IconData?;
        final isSelected = _selectedFilter == label;

        return FilterChip(
          label: Text(label),
          avatar: icon != null ? Icon(icon, size: 14) : null,
          selected: isSelected,
          onSelected: (selected) {
            setState(() => _selectedFilter = label);
            // TODO: Implement filter functionality
            debugPrint('TODO: Filter by: $label');
          },
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

  Widget _buildMainContent(ThemeData theme, ColorScheme colorScheme) {
    if (_currentContent == null) {
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
          _buildArticleContent(theme, colorScheme, _currentContent!),
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

  Widget _buildArticleContent(
    ThemeData theme,
    ColorScheme colorScheme,
    SectionContent content,
  ) {
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
            _buildMetadata(theme, colorScheme, content.metadata!),
          ],
        ],
      ),
    );
  }

  Widget _buildMetadata(
    ThemeData theme,
    ColorScheme colorScheme,
    SectionMetadata metadata,
  ) {
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
              child: _buildMetadataItem(
                'ORIGINAL SOURCE',
                metadata.originalSource!,
                colorScheme,
                isLink: true,
              ),
            ),
          if (metadata.authorizingBody != null)
            Expanded(
              child: _buildMetadataItem(
                'AUTHORIZING BODY',
                metadata.authorizingBody!,
                colorScheme,
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

  Widget _buildMetadataItem(
    String label,
    String value,
    ColorScheme colorScheme, {
    bool isLink = false,
  }) {
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
          onTap: isLink
              ? () {
                  // TODO: Handle link tap
                  debugPrint('TODO: Open source: $value');
                }
              : null,
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

  // Event Handlers
  void _handleNodeSelected(SectionNode node) {
    if (_selectedNodeId == node.id) return;

    setState(() {
      _selectedNodeId = node.id;
      _currentContent = _mapNodeToContent(node);
    });

    // TODO: Replace with API call later
    debugPrint('Load content for node: ${node.id}');
  }

  void _handleDocumentChanged(String document) {
    setState(() {
      _selectedNodeId = null;
      _currentContent = null;
      _hierarchyNodes = [];
    });

    debugPrint('Load document: $document');
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

  SectionContent? _mapNodeToContent(SectionNode node) {
    // Only show content for article-level or deeper (optional rule)
    if (node.type == SectionNodeType.chapter ||
        node.type == SectionNodeType.section) {
      return SectionContent(
        id: node.id,
        title: node.title,
        reference: 'STRUCTURE',
        type: 'Hierarchy',
        content: 'Đây là mục cấu trúc: ${node.title}',
        paragraphs: [],
        status: SectionStatus.effective,
        metadata: SectionMetadata(
          authorizingBody: 'System',
          tags: ['Structure'],
        ),
      );
    }

    return SectionContent(
      id: node.id,
      title:
          '${node.title}${node.subtitle != null ? '. ${node.subtitle}' : ''}',
      reference: 'AUTO/${node.id.toUpperCase()}',
      type: node.type.name,
      content:
          'Nội dung của ${node.title}. Đây là dữ liệu giả lập để hiển thị nội dung điều khoản.',
      paragraphs: [
        'Khoản 1: Nội dung chi tiết cho ${node.title}.',
        'Khoản 2: Quy định bổ sung liên quan đến ${node.title}.',
      ],
      status: SectionStatus.effective,
      revisionDate: '2024',
      metadata: SectionMetadata(
        originalSource: 'Generated Mock Data',
        authorizingBody: 'Quốc hội Việt Nam',
        tags: [node.type.name],
      ),
    );
  }
}
