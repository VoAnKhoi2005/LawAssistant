import 'package:flutter/material.dart';

/// Document Management Screen - Full Width Layout
/// Based on: law_assistant_demo/document_management_full_width/code.html
class DocumentManagementFullWidthScreen extends StatefulWidget {
  const DocumentManagementFullWidthScreen({Key? key}) : super(key: key);

  @override
  State<DocumentManagementFullWidthScreen> createState() =>
      _DocumentManagementFullWidthScreenState();
}

class _DocumentManagementFullWidthScreenState
    extends State<DocumentManagementFullWidthScreen> {
  String _selectedFilter = 'All';

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      backgroundColor: colorScheme.surface,
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(theme, colorScheme),
          _buildFilters(theme, colorScheme),
          Expanded(child: _buildContent(theme, colorScheme)),
        ],
      ),
    );
  }

  Widget _buildHeader(ThemeData theme, ColorScheme colorScheme) {
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
                ),
              ),
              const SizedBox(width: 12),
              FilledButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.upload_file, size: 20),
                label: const Text('Add Document'),
                style: FilledButton.styleFrom(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
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

  Widget _buildFilters(ThemeData theme, ColorScheme colorScheme) {
    final filters = ['All', 'Laws', 'Decrees', 'Circulars', 'Decisions'];

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
          ...filters.map(
            (filter) => Padding(
              padding: const EdgeInsets.only(right: 8),
              child: FilterChip(
                label: Text(filter),
                selected: _selectedFilter == filter,
                onSelected: (selected) {
                  setState(() => _selectedFilter = filter);
                },
                backgroundColor: colorScheme.surfaceContainerHigh,
                selectedColor: colorScheme.secondary,
                labelStyle: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: _selectedFilter == filter
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
            onPressed: () {},
            icon: const Icon(Icons.filter_list, size: 16),
            label: const Text('Advanced'),
          ),
          const SizedBox(width: 16),
          TextButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.sort, size: 16),
            label: const Text('Sort'),
          ),
        ],
      ),
    );
  }

  Widget _buildContent(ThemeData theme, ColorScheme colorScheme) {
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
              child: ListView(
                children: [
                  _buildDocumentRow(
                    theme,
                    colorScheme,
                    id: 'LAW-2023-01',
                    number: '15/2023/QH15',
                    title: 'Luật Đấu thầu 2023',
                    field: 'Field: Bidding, Public Asset Management',
                    date: '01/01/2024',
                    status: 'Active',
                    statusColor: colorScheme.tertiary,
                    icon: Icons.picture_as_pdf,
                    iconBgColor: const Color(0xFFFFEBEE),
                    iconColor: const Color(0xFF9E3F4E),
                  ),
                  const SizedBox(height: 16),
                  _buildDocumentRow(
                    theme,
                    colorScheme,
                    id: 'DEC-2023-45',
                    number: '24/2023/NĐ-CP',
                    title:
                        'Nghị định quy định chi tiết một số điều của Luật Đấu thầu',
                    field: 'Field: Administrative, Specialized Law',
                    date: '27/02/2024',
                    status: 'Active',
                    statusColor: colorScheme.tertiary,
                    icon: Icons.description,
                    iconBgColor: colorScheme.secondaryContainer,
                    iconColor: colorScheme.secondary,
                  ),
                  const SizedBox(height: 16),
                  _buildDocumentRow(
                    theme,
                    colorScheme,
                    id: 'LAW-2015-12',
                    number: '100/2015/QH13',
                    title: 'Bộ luật Hình sự 2015 (Sửa đổi 2017)',
                    field: 'Field: Judicial, Criminal',
                    date: '01/01/2018',
                    status: 'Expired (Replaced)',
                    statusColor: colorScheme.onSurfaceVariant,
                    icon: Icons.picture_as_pdf,
                    iconBgColor: const Color(0xFFFFEBEE),
                    iconColor: const Color(0xFF9E3F4E),
                  ),
                ],
              ),
            ),
            _buildPagination(theme, colorScheme),
          ],
        ),
      ),
    );
  }

  Widget _buildDocumentRow(
    ThemeData theme,
    ColorScheme colorScheme, {
    required String id,
    required String number,
    required String title,
    required String field,
    required String date,
    required String status,
    required Color statusColor,
    required IconData icon,
    required Color iconBgColor,
    required Color iconColor,
  }) {
    return Container(
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
                  'ID: $id',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: colorScheme.primary,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  number,
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            flex: 6,
            child: Row(
              children: [
                Container(
                  width: 32,
                  height: 40,
                  decoration: BoxDecoration(
                    color: iconBgColor,
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(
                      color: iconColor.withOpacity(0.2),
                    ),
                  ),
                  alignment: Alignment.center,
                  child: Icon(icon, color: iconColor, size: 20),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        field,
                        style: TextStyle(
                          fontSize: 11,
                          color: colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            flex: 3,
            child: Text(
              date,
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
                status,
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
          Expanded(
            flex: 2,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                IconButton(
                  icon: const Icon(Icons.edit, size: 18),
                  color: colorScheme.primary,
                  onPressed: () {},
                ),
                IconButton(
                  icon: const Icon(Icons.delete, size: 18),
                  color: colorScheme.error,
                  onPressed: () {},
                ),
                IconButton(
                  icon: const Icon(Icons.more_vert, size: 18),
                  color: colorScheme.onSurfaceVariant,
                  onPressed: () {},
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPagination(ThemeData theme, ColorScheme colorScheme) {
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
                  text: '3',
                  style: TextStyle(
                    fontWeight: FontWeight.w700,
                    color: colorScheme.onSurface,
                  ),
                ),
                const TextSpan(text: ' of '),
                TextSpan(
                  text: '1,248',
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
                onPressed: () {},
              ),
              _buildPageButton('1', colorScheme, isSelected: true),
              _buildPageButton('2', colorScheme),
              _buildPageButton('3', colorScheme),
              IconButton(
                icon: const Icon(Icons.chevron_right, size: 18),
                onPressed: () {},
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPageButton(String page, ColorScheme colorScheme,
      {bool isSelected = false}) {
    return Container(
      width: 32,
      height: 32,
      margin: const EdgeInsets.symmetric(horizontal: 4),
      decoration: BoxDecoration(
        color: isSelected ? colorScheme.primary : Colors.transparent,
        borderRadius: BorderRadius.circular(8),
      ),
      alignment: Alignment.center,
      child: Text(
        page,
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w700,
          color: isSelected ? Colors.white : colorScheme.onSurface,
        ),
      ),
    );
  }
}
