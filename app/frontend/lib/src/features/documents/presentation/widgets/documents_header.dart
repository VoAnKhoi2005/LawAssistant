import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../../core/api/services/upload_file_api_service.dart';
import '../providers/documents_provider.dart';
import 'create_document_dialog.dart';

class DocumentsHeader extends StatelessWidget {
  final bool isMobile;
  
  const DocumentsHeader({super.key, this.isMobile = false});

  Future<void> _handleAddDocument(BuildContext context) async {
    final uploadFileService = UploadFileApiService(
      context.read<DocumentsProvider>().documentService.apiClient,
    );

    // Show create document dialog directly
    showDialog(
      context: context,
      builder: (dialogContext) => CreateDocumentDialog(
        uploadFileService: uploadFileService,
        onSubmit: (request) async {
          Navigator.of(dialogContext).pop();
          
          // Show loading snackbar
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Row(
                children: [
                  SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  ),
                  SizedBox(width: 12),
                  Text('Đang tạo văn bản...'),
                ],
              ),
              duration: Duration(seconds: 30),
            ),
          );
          
          final provider = context.read<DocumentsProvider>();
          final success = await provider.createDocument(request);
          
          // Hide loading snackbar
          if (context.mounted) {
            ScaffoldMessenger.of(context).hideCurrentSnackBar();
          }
          
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(
                  success
                      ? 'Tạo văn bản thành công'
                      : provider.errorMessage ?? 'Không thể tạo văn bản',
                ),
                backgroundColor: success ? Colors.green : Colors.red,
              ),
            );
          }
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Padding(
      padding: EdgeInsets.fromLTRB(
        isMobile ? 16 : 40,
        isMobile ? 16 : 40,
        isMobile ? 16 : 40,
        isMobile ? 12 : 24,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isMobile)
            Row(
              children: [
                Text(
                  'VIETNAM LEGAL ARCHIVE',
                  style: theme.textTheme.labelSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    letterSpacing: 2,
                    color: theme.colorScheme.primary,
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  height: 4,
                  width: 32,
                  decoration: BoxDecoration(
                    color: theme.colorScheme.tertiary,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ],
            ),
          SizedBox(height: isMobile ? 0 : 8),
          Text(
            'Quản lý Văn bản Pháp luật',
            style: theme.textTheme.headlineLarge?.copyWith(
              fontSize: isMobile ? 24 : 36,
              fontWeight: FontWeight.w900,
              height: 1.2,
            ),
          ),
          if (!isMobile) ...[
            const SizedBox(height: 8),
            Text(
              'Hệ thống lưu trữ và tra cứu tri thức pháp luật tập trung dành cho tổ chức hành nghề luật.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
          const SizedBox(height: 16),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              SizedBox(
                width: isMobile ? double.infinity : 256,
                child: TextField(
                  decoration: InputDecoration(
                    hintText: 'Tìm kiếm văn bản...',
                    prefixIcon: const Icon(Icons.search, size: 20),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(16),
                      borderSide: BorderSide.none,
                    ),
                    filled: true,
                    fillColor: theme.colorScheme.surfaceContainerLow,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 12,
                    ),
                  ),
                ),
              ),
              SizedBox(
                width: isMobile ? double.infinity : null,
                child: FilledButton.icon(
                  onPressed: () => _handleAddDocument(context),
                  icon: const Icon(Icons.upload_file, size: 18),
                  label: const Text('Thêm văn bản'),
                  style: FilledButton.styleFrom(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 12,
                    ),
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
