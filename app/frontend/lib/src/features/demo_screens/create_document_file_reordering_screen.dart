import 'package:flutter/material.dart';

/// Create Document File Reordering Screen with Modal
/// Based on: law_assistant_demo/create_document_file_reordering/code.html
class CreateDocumentFileReorderingScreen extends StatefulWidget {
  const CreateDocumentFileReorderingScreen({Key? key}) : super(key: key);

  @override
  State<CreateDocumentFileReorderingScreen> createState() =>
      _CreateDocumentFileReorderingScreenState();
}

class _CreateDocumentFileReorderingScreenState
    extends State<CreateDocumentFileReorderingScreen> {
  bool _showModal = true;
  final List<FileItem> _files = [
    FileItem(
      name: 'Draft_v1.pdf',
      size: '1.2 MB',
      date: 'Added today',
      icon: Icons.picture_as_pdf,
      iconColor: const Color(0xFF9E3F4E),
    ),
    FileItem(
      name: 'Legal_Brief_Final.docx',
      size: '842 KB',
      date: 'Added today',
      icon: Icons.description,
      iconColor: const Color(0xFF48617E),
    ),
    FileItem(
      name: 'Exhibit_A.pdf',
      size: '4.5 MB',
      date: 'Added today',
      icon: Icons.picture_as_pdf,
      iconColor: const Color(0xFF9E3F4E),
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      backgroundColor: colorScheme.surface,
      body: Stack(
        children: [
          _buildBackgroundContent(theme, colorScheme),
          if (_showModal) _buildModal(theme, colorScheme),
        ],
      ),
    );
  }

  Widget _buildBackgroundContent(ThemeData theme, ColorScheme colorScheme) {
    return Opacity(
      opacity: _showModal ? 0.5 : 1.0,
      child: IgnorePointer(
        ignoring: _showModal,
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Case Documents',
                        style: theme.textTheme.headlineLarge?.copyWith(
                          fontSize: 30,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Organize and analyze litigation artifacts for the Smith vs. Global Tech case.',
                        style: TextStyle(
                          color: colorScheme.onSurfaceVariant,
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                  FilledButton(
                    onPressed: () {},
                    style: FilledButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 24,
                        vertical: 20,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: const Text('New Case'),
                  ),
                ],
              ),
              const SizedBox(height: 48),
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color: colorScheme.surfaceContainerLow,
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildModal(ThemeData theme, ColorScheme colorScheme) {
    return Container(
      color: Colors.black.withOpacity(0.4),
      alignment: Alignment.center,
      child: Container(
        width: 672,
        constraints: const BoxConstraints(maxHeight: 800),
        margin: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: colorScheme.surfaceContainerLowest,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: const Color(0xFF525F71).withOpacity(0.15),
              blurRadius: 48,
              offset: const Offset(0, 24),
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildModalHeader(theme, colorScheme),
            Flexible(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(32),
                child: _buildModalBody(theme, colorScheme),
              ),
            ),
            _buildModalFooter(theme, colorScheme),
          ],
        ),
      ),
    );
  }

  Widget _buildModalHeader(ThemeData theme, ColorScheme colorScheme) {
    return Container(
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        border: Border(
          bottom: BorderSide(
            color: colorScheme.outlineVariant.withOpacity(0.1),
          ),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Create New Document',
                style: theme.textTheme.titleLarge?.copyWith(
                  fontSize: 20,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'Step 2 of 2: Review and Arrange Files',
                style: TextStyle(
                  fontSize: 12,
                  color: colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
          IconButton(
            onPressed: () {
              setState(() => _showModal = false);
            },
            icon: const Icon(Icons.close),
            style: IconButton.styleFrom(
              backgroundColor: Colors.transparent,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildModalBody(ThemeData theme, ColorScheme colorScheme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildDocumentInfo(theme, colorScheme),
        const SizedBox(height: 32),
        _buildFilesSection(theme, colorScheme),
        const SizedBox(height: 32),
        _buildInfoNote(theme, colorScheme),
      ],
    );
  }

  Widget _buildDocumentInfo(ThemeData theme, ColorScheme colorScheme) {
    return Column(
      children: [
        _buildTextField(
          'DOCUMENT TITLE',
          'Legal Brief for Smith vs. Global Tech (Initial Filings)',
          colorScheme,
          borderColor: colorScheme.primary,
        ),
        const SizedBox(height: 24),
        Row(
          children: [
            Expanded(
              child: _buildTextField(
                'CASE ID',
                'CV-2024-0082',
                colorScheme,
              ),
            ),
            const SizedBox(width: 24),
            Expanded(
              child: _buildTextField(
                'AUTHOR',
                'Doe, J.',
                colorScheme,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildTextField(
    String label,
    String value,
    ColorScheme colorScheme, {
    Color? borderColor,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w700,
            color: colorScheme.onSurfaceVariant,
            letterSpacing: 1.5,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: TextEditingController(text: value),
          readOnly: true,
          style: TextStyle(
            fontWeight: label == 'DOCUMENT TITLE'
                ? FontWeight.w600
                : FontWeight.w400,
            color: colorScheme.onSurface,
          ),
          decoration: InputDecoration(
            border: UnderlineInputBorder(
              borderSide: BorderSide(
                color: borderColor ?? colorScheme.outlineVariant.withOpacity(0.3),
              ),
            ),
            enabledBorder: UnderlineInputBorder(
              borderSide: BorderSide(
                color: borderColor ?? colorScheme.outlineVariant.withOpacity(0.3),
              ),
            ),
            focusedBorder: UnderlineInputBorder(
              borderSide: BorderSide(
                color: borderColor ?? colorScheme.primary,
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildFilesSection(ThemeData theme, ColorScheme colorScheme) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'UPLOADED FILES (${_files.length})',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w700,
                color: colorScheme.onSurface,
                letterSpacing: 0.5,
              ),
            ),
            TextButton.icon(
              onPressed: () {},
              icon: const Icon(Icons.add, size: 14),
              label: const Text('Add more'),
              style: TextButton.styleFrom(
                foregroundColor: colorScheme.primary,
                textStyle: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        ReorderableListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: _files.length,
          onReorder: (oldIndex, newIndex) {
            setState(() {
              if (newIndex > oldIndex) newIndex--;
              final item = _files.removeAt(oldIndex);
              _files.insert(newIndex, item);
            });
          },
          itemBuilder: (context, index) {
            final file = _files[index];
            final isLast = index == _files.length - 1;
            
            return _buildFileItem(
              key: ValueKey(file.name),
              theme,
              colorScheme,
              file,
              index,
              isLast,
            );
          },
        ),
      ],
    );
  }

  Widget _buildFileItem(
    ThemeData theme,
    ColorScheme colorScheme,
    FileItem file,
    int index,
    bool isLast, {
    Key? key,
  }) {
    return Container(
      key: key,
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerLow,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Colors.transparent,
        ),
      ),
      child: Row(
        children: [
          Icon(
            Icons.drag_indicator,
            color: colorScheme.outlineVariant,
            size: 20,
          ),
          const SizedBox(width: 16),
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: file.icon == Icons.picture_as_pdf
                  ? const Color(0xFFFFEBEE)
                  : const Color(0xFFE3F2FD),
              borderRadius: BorderRadius.circular(8),
            ),
            alignment: Alignment.center,
            child: Icon(
              file.icon,
              color: file.iconColor,
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  file.name,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '${file.size} • ${file.date}',
                  style: TextStyle(
                    fontSize: 10,
                    color: colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            onPressed: index > 0 ? () => _moveFile(index, index - 1) : null,
            icon: const Icon(Icons.arrow_upward, size: 18),
            color: colorScheme.onSurfaceVariant,
          ),
          IconButton(
            onPressed: !isLast ? () => _moveFile(index, index + 1) : null,
            icon: Icon(
              Icons.arrow_downward,
              size: 18,
            ),
            color: !isLast ? colorScheme.onSurfaceVariant : null,
            disabledColor: colorScheme.onSurfaceVariant.withOpacity(0.2),
          ),
          const SizedBox(width: 8),
          IconButton(
            onPressed: () {
              setState(() => _files.removeAt(index));
            },
            icon: const Icon(Icons.delete, size: 18),
            color: colorScheme.error,
          ),
        ],
      ),
    );
  }

  void _moveFile(int from, int to) {
    setState(() {
      final item = _files.removeAt(from);
      _files.insert(to, item);
    });
  }

  Widget _buildInfoNote(ThemeData theme, ColorScheme colorScheme) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.tertiaryContainer.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: colorScheme.tertiaryContainer.withOpacity(0.2),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            Icons.info_outline,
            color: colorScheme.tertiary,
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              'The order of files above will determine the structure of the final compiled document. You can drag and drop items to adjust the sequence.',
              style: TextStyle(
                fontSize: 12,
                color: colorScheme.onTertiaryContainer,
                height: 1.5,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildModalFooter(ThemeData theme, ColorScheme colorScheme) {
    return Container(
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerLow.withOpacity(0.5),
        border: Border(
          top: BorderSide(
            color: colorScheme.outlineVariant.withOpacity(0.1),
          ),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          TextButton(
            onPressed: () {},
            child: const Text('Back'),
          ),
          Row(
            children: [
              TextButton(
                onPressed: () {
                  setState(() => _showModal = false);
                },
                child: const Text('Cancel'),
              ),
              const SizedBox(width: 16),
              FilledButton(
                onPressed: () {},
                style: FilledButton.styleFrom(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 32,
                    vertical: 20,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text('Create Document'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class FileItem {
  final String name;
  final String size;
  final String date;
  final IconData icon;
  final Color iconColor;

  FileItem({
    required this.name,
    required this.size,
    required this.date,
    required this.icon,
    required this.iconColor,
  });
}
