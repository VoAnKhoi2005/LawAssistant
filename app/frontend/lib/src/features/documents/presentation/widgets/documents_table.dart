import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../providers/documents_provider.dart';
import '../../../../core/constants/breakpoints.dart';

class DocumentsTable extends StatelessWidget {
  const DocumentsTable({super.key});

  Future<void> _handleEdit(BuildContext context, dynamic doc) async {
    // TODO: Implement edit functionality
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Chỉnh sửa "${doc.title}"'),
      ),
    );
  }

  Future<void> _handleDelete(BuildContext context, String id, String title) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Xác nhận xóa'),
        content: Text('Bạn có chắc chắn muốn xóa "$title"?\nHành động này không thể hoàn tác.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Hủy'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
            child: const Text('Xóa'),
          ),
        ],
      ),
    );

    if (confirmed == true && context.mounted) {
      final provider = context.read<DocumentsProvider>();
      final success = await provider.deleteDocument(id);

      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              success
                  ? 'Xóa văn bản thành công'
                  : provider.errorMessage ?? 'Không thể xóa văn bản',
            ),
            backgroundColor: success
                ? Colors.green
                : Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return LayoutBuilder(
      builder: (context, constraints) {
        final breakpoints = Breakpoints(constraints.maxWidth);
        
        return Padding(
          padding: EdgeInsets.fromLTRB(
            breakpoints.isMobile ? 8 : 40,
            0,
            breakpoints.isMobile ? 8 : 40,
            breakpoints.isMobile ? 8 : 40,
          ),
          child: Container(
            decoration: BoxDecoration(
              color: theme.colorScheme.surfaceContainerLow,
              borderRadius: BorderRadius.circular(breakpoints.isMobile ? 16 : 32),
            ),
            padding: EdgeInsets.all(breakpoints.isMobile ? 8 : 16),
            child: Column(
              children: [
                Expanded(
                  child: Consumer<DocumentsProvider>(
                    builder: (context, provider, _) {
                      if (provider.state == DocumentsLoadingState.loading) {
                        return const Center(child: CircularProgressIndicator());
                      }

                      if (provider.state == DocumentsLoadingState.error) {
                        return Center(
                          child: Text(provider.errorMessage ?? 'Error'),
                        );
                      }

                      if (provider.documents.isEmpty) {
                        return const Center(
                          child: Text('Chưa có văn bản nào'),
                        );
                      }

                      // Mobile card view
                      if (breakpoints.isMobile) {
                        return ListView.builder(
                          itemCount: provider.documents.length,
                          itemBuilder: (context, index) {
                            final doc = provider.documents[index];
                            return Card(
                              margin: const EdgeInsets.only(bottom: 8),
                              child: ListTile(
                                leading: Container(
                                  width: 40,
                                  height: 40,
                                  decoration: BoxDecoration(
                                    color: theme.colorScheme.error.withOpacity(0.1),
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Icon(
                                    Icons.picture_as_pdf,
                                    color: theme.colorScheme.error,
                                    size: 20,
                                  ),
                                ),
                                title: Text(
                                  doc.title,
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                subtitle: Text(doc.soHieu),
                                trailing: PopupMenuButton(
                                  itemBuilder: (context) => [
                                    const PopupMenuItem(
                                      value: 'edit',
                                      child: Row(
                                        children: [
                                          Icon(Icons.edit),
                                          SizedBox(width: 8),
                                          Text('Chỉnh sửa'),
                                        ],
                                      ),
                                    ),
                                    const PopupMenuItem(
                                      value: 'delete',
                                      child: Row(
                                        children: [
                                          Icon(Icons.delete),
                                          SizedBox(width: 8),
                                          Text('Xóa'),
                                        ],
                                      ),
                                    ),
                                  ],
                                  onSelected: (value) {
                                    if (value == 'edit') {
                                      _handleEdit(context, doc);
                                    } else if (value == 'delete' && doc.id?.value != null) {
                                      _handleDelete(context, doc.id!.value, doc.title);
                                    }
                                  },
                                ),
                              ),
                            );
                          },
                        );
                      }

                      // Desktop table view
                      return SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: ConstrainedBox(
                          constraints: BoxConstraints(
                            minWidth: constraints.maxWidth - (breakpoints.isMobile ? 16 : 32),
                          ),
                          child: DataTable(
                            headingRowHeight: 48,
                            dataRowMinHeight: 72,
                            dataRowMaxHeight: 72,
                            columnSpacing: 24,
                            horizontalMargin: 24,
                            headingTextStyle: theme.textTheme.labelSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                              letterSpacing: 1.5,
                              color: theme.colorScheme.onSurfaceVariant.withOpacity(0.6),
                            ),
                            columns: const [
                              DataColumn(label: Text('ID & SỐ HIỆU')),
                              DataColumn(label: Text('TIÊU ĐỀ VĂN BẢN')),
                              DataColumn(label: Text('NGÀY HIỆU LỰC')),
                              DataColumn(label: Text('TRẠNG THÁI')),
                              DataColumn(label: Text('THAO TÁC')),
                            ],
                            rows: provider.documents.map((doc) {
                              return DataRow(
                                cells: [
                                  DataCell(
                                    Column(
                                      mainAxisAlignment: MainAxisAlignment.center,
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          'ID: ${doc.id?.value ?? "N/A"}',
                                          style: theme.textTheme.labelSmall?.copyWith(
                                            fontWeight: FontWeight.bold,
                                            color: theme.colorScheme.primary,
                                          ),
                                        ),
                                        Text(
                                          doc.soHieu,
                                          style: theme.textTheme.titleSmall?.copyWith(
                                            fontWeight: FontWeight.w900,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  DataCell(
                                    Row(
                                      children: [
                                        Container(
                                          width: 32,
                                          height: 40,
                                          decoration: BoxDecoration(
                                            color: theme.colorScheme.error.withOpacity(0.1),
                                            border: Border.all(
                                              color: theme.colorScheme.error.withOpacity(0.2),
                                            ),
                                            borderRadius: BorderRadius.circular(6),
                                          ),
                                          child: Icon(
                                            Icons.picture_as_pdf,
                                            color: theme.colorScheme.error,
                                            size: 20,
                                          ),
                                        ),
                                        const SizedBox(width: 12),
                                        Expanded(
                                          child: Column(
                                            mainAxisAlignment: MainAxisAlignment.center,
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Text(
                                                doc.title,
                                                style: theme.textTheme.bodyMedium?.copyWith(
                                                  fontWeight: FontWeight.w600,
                                                ),
                                                maxLines: 1,
                                                overflow: TextOverflow.ellipsis,
                                              ),
                                              if (doc.linhVuc != null)
                                                Text(
                                                  'Lĩnh vực: ${doc.linhVuc}',
                                                  style: theme.textTheme.labelSmall?.copyWith(
                                                    color: theme.colorScheme.onSurfaceVariant,
                                                  ),
                                                  maxLines: 1,
                                                  overflow: TextOverflow.ellipsis,
                                                ),
                                            ],
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  DataCell(
                                    Text(
                                      doc.ngayHieuLuc != null
                                          ? DateFormat('dd/MM/yyyy').format(doc.ngayHieuLuc!)
                                          : 'N/A',
                                      style: theme.textTheme.bodyMedium?.copyWith(
                                        color: theme.colorScheme.onSurfaceVariant,
                                      ),
                                    ),
                                  ),
                                  DataCell(
                                    Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 10,
                                        vertical: 4,
                                      ),
                                      decoration: BoxDecoration(
                                        color: theme.colorScheme.tertiaryContainer.withOpacity(0.1),
                                        borderRadius: BorderRadius.circular(12),
                                      ),
                                      child: Text(
                                        doc.trangThai ?? 'Đang có hiệu lực',
                                        style: theme.textTheme.labelSmall?.copyWith(
                                          fontWeight: FontWeight.bold,
                                          color: theme.colorScheme.tertiary,
                                          letterSpacing: 0.5,
                                        ),
                                      ),
                                    ),
                                  ),
                                  DataCell(
                                    Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        IconButton(
                                          icon: const Icon(Icons.edit, size: 18),
                                          onPressed: () => _handleEdit(context, doc),
                                          color: theme.colorScheme.primary,
                                          tooltip: 'Chỉnh sửa',
                                        ),
                                        IconButton(
                                          icon: const Icon(Icons.delete, size: 18),
                                          onPressed: () {
                                            if (doc.id?.value != null) {
                                              _handleDelete(context, doc.id!.value, doc.title);
                                            }
                                          },
                                          color: theme.colorScheme.error,
                                          tooltip: 'Xóa',
                                        ),
                                        IconButton(
                                          icon: const Icon(Icons.more_vert, size: 18),
                                          onPressed: () {},
                                          tooltip: 'Thêm',
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              );
                            }).toList(),
                          ),
                        ),
                      );
                    },
                  ),
                ),
                // Pagination
                Consumer<DocumentsProvider>(
                  builder: (context, provider, _) {
                    return Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Row(
                        children: [
                          if (!breakpoints.isMobile)
                            Text(
                              'Hiển thị ${provider.documents.length} văn bản',
                              style: theme.textTheme.labelSmall?.copyWith(
                                color: theme.colorScheme.onSurfaceVariant,
                              ),
                            ),
                          const Spacer(),
                          IconButton(
                            onPressed: provider.hasPrevPage
                                ? () => provider.prevPage()
                                : null,
                            icon: const Icon(Icons.chevron_left),
                          ),
                          Text(
                            'Trang ${provider.currentPage}',
                            style: theme.textTheme.labelMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          IconButton(
                            onPressed: provider.hasNextPage
                                ? () => provider.nextPage()
                                : null,
                            icon: const Icon(Icons.chevron_right),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}