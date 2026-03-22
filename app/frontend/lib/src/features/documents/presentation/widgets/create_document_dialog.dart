import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:file_selector/file_selector.dart';
import '../../../../core/api/models/document_models.dart';
import '../../../../core/api/services/upload_file_api_service.dart';

class CreateDocumentDialog extends StatefulWidget {
  final UploadFileApiService uploadFileService;
  final Function(CreateDocumentRequest request) onSubmit;

  const CreateDocumentDialog({
    super.key,
    required this.uploadFileService,
    required this.onSubmit,
  });

  @override
  State<CreateDocumentDialog> createState() => _CreateDocumentDialogState();
}

class _CreateDocumentDialogState extends State<CreateDocumentDialog> {
  final _formKey = GlobalKey<FormState>();
  final _soHieuController = TextEditingController();
  final _titleController = TextEditingController();
  DateTime _effectiveDate = DateTime.now();
  final List<_UploadedFileInfo> _uploadedFiles = [];
  bool _isUploading = false;

  @override
  void dispose() {
    _soHieuController.dispose();
    _titleController.dispose();
    super.dispose();
  }

  Future<void> _pickFiles() async {
    final result = await openFiles(
      acceptedTypeGroups: [
        const XTypeGroup(
          label: 'PDF Documents',
          extensions: ['pdf'],
        ),
      ],
    );

    if (result.isEmpty) return;

    setState(() => _isUploading = true);

    // Upload each file immediately
    for (final file in result) {
      try {
        final response = await widget.uploadFileService.uploadFile(
          file.path,
          file.name,
        );

        if (response.success && response.data?.id?.value != null) {
          final uploadedFile = _UploadedFileInfo(
            id: response.data!.id!.value,
            filename: file.name,
            size: await file.length(),
          );
          
          setState(() {
            _uploadedFiles.add(uploadedFile);
          });
        } else {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Không thể tải lên: ${file.name}'),
                backgroundColor: Colors.red,
              ),
            );
          }
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Lỗi khi tải lên: ${file.name}'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }

    setState(() => _isUploading = false);
  }

  void _removeFile(int index) {
    setState(() {
      _uploadedFiles.removeAt(index);
    });
  }

  Future<void> _handleSubmit() async {
    if (_formKey.currentState?.validate() ?? false) {
      if (_uploadedFiles.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Vui lòng chọn ít nhất một tệp'),
            backgroundColor: Colors.orange,
          ),
        );
        return;
      }

      // Create document with already uploaded file IDs
      final request = CreateDocumentRequest(
        soHieu: _soHieuController.text.trim(),
        title: _titleController.text.trim(),
        effectiveDate: DateFormat('yyyy-MM-dd').format(_effectiveDate),
        fileIds: _uploadedFiles.map((f) => f.id).toList(),
      );

      widget.onSubmit(request);
    }
  }

  Future<void> _selectDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _effectiveDate,
      firstDate: DateTime(1900),
      lastDate: DateTime(2100),
      locale: const Locale('vi', 'VN'),
    );

    if (picked != null) {
      setState(() {
        _effectiveDate = picked;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Dialog(
      child: Container(
        width: 600,
        constraints: const BoxConstraints(maxHeight: 700),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Header
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: theme.colorScheme.primaryContainer,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(28),
                  topRight: Radius.circular(28),
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.add_circle_outline,
                    color: theme.colorScheme.onPrimaryContainer,
                    size: 32,
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Text(
                      'Tạo văn bản mới',
                      style: theme.textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: theme.colorScheme.onPrimaryContainer,
                      ),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.of(context).pop(),
                    color: theme.colorScheme.onPrimaryContainer,
                  ),
                ],
              ),
            ),
            // Content
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildSoHieuField(theme),
                      const SizedBox(height: 16),
                      _buildTitleField(theme),
                      const SizedBox(height: 16),
                      _buildEffectiveDateField(theme),
                      const SizedBox(height: 24),
                      _buildFileSelection(theme),
                    ],
                  ),
                ),
              ),
            ),
            // Footer
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: theme.colorScheme.surfaceContainerLow,
                borderRadius: const BorderRadius.only(
                  bottomLeft: Radius.circular(28),
                  bottomRight: Radius.circular(28),
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  OutlinedButton(
                    onPressed: () => Navigator.of(context).pop(),
                    child: const Text('Hủy'),
                  ),
                  const SizedBox(width: 12),
                  FilledButton.icon(
                    onPressed: _handleSubmit,
                    icon: const Icon(Icons.check, size: 20),
                    label: const Text('Tạo văn bản'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSoHieuField(ThemeData theme) {
    return TextFormField(
      controller: _soHieuController,
      decoration: InputDecoration(
        labelText: 'Số hiệu văn bản *',
        hintText: 'Ví dụ: 01/2013/QH13',
        prefixIcon: const Icon(Icons.numbers),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        filled: true,
        fillColor: theme.colorScheme.surfaceContainerHighest,
      ),
      validator: (value) {
        if (value == null || value.trim().isEmpty) {
          return 'Vui lòng nhập số hiệu';
        }
        return null;
      },
    );
  }

  Widget _buildTitleField(ThemeData theme) {
    return TextFormField(
      controller: _titleController,
      decoration: InputDecoration(
        labelText: 'Tiêu đề văn bản *',
        hintText: 'Nhập tiêu đề văn bản pháp luật',
        prefixIcon: const Icon(Icons.title),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        filled: true,
        fillColor: theme.colorScheme.surfaceContainerHighest,
      ),
      maxLines: 3,
      validator: (value) {
        if (value == null || value.trim().isEmpty) {
          return 'Vui lòng nhập tiêu đề';
        }
        return null;
      },
    );
  }

  Widget _buildEffectiveDateField(ThemeData theme) {
    return InkWell(
      onTap: _selectDate,
      child: InputDecorator(
        decoration: InputDecoration(
          labelText: 'Ngày hiệu lực *',
          prefixIcon: const Icon(Icons.calendar_today),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          filled: true,
          fillColor: theme.colorScheme.surfaceContainerHighest,
        ),
        child: Text(
          DateFormat('dd/MM/yyyy').format(_effectiveDate),
          style: theme.textTheme.bodyLarge,
        ),
      ),
    );
  }

  Widget _buildFileSelection(ThemeData theme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(
              Icons.attach_file,
              color: theme.colorScheme.primary,
              size: 20,
            ),
            const SizedBox(width: 8),
            Text(
              'Chọn tệp đính kèm *',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const Spacer(),
            if (_isUploading)
              const SizedBox(
                width: 16,
                height: 16,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            else
              Text(
                '${_uploadedFiles.length} đã tải lên',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.primary,
                  fontWeight: FontWeight.bold,
                ),
              ),
          ],
        ),
        const SizedBox(height: 12),
        OutlinedButton.icon(
          onPressed: _isUploading ? null : _pickFiles,
          icon: _isUploading
              ? const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.upload_file),
          label: Text(_isUploading ? 'Đang tải lên...' : 'Chọn & Tải lên tệp PDF'),
          style: OutlinedButton.styleFrom(
            minimumSize: const Size(double.infinity, 48),
          ),
        ),
        if (_uploadedFiles.isNotEmpty) ...[
          const SizedBox(height: 12),
          Container(
            constraints: const BoxConstraints(maxHeight: 200),
            decoration: BoxDecoration(
              border: Border.all(
                color: theme.colorScheme.outline.withOpacity(0.5),
              ),
              borderRadius: BorderRadius.circular(12),
            ),
            child: ListView.separated(
              shrinkWrap: true,
              itemCount: _uploadedFiles.length,
              separatorBuilder: (context, index) => Divider(
                height: 1,
                color: theme.colorScheme.outline.withOpacity(0.2),
              ),
              itemBuilder: (context, index) {
                final file = _uploadedFiles[index];
                return ListTile(
                  leading: Icon(
                    Icons.check_circle,
                    color: Colors.green,
                  ),
                  title: Text(
                    file.filename,
                    style: theme.textTheme.bodyMedium,
                  ),
                  subtitle: Text(
                    _formatFileSize(file.size),
                    style: theme.textTheme.bodySmall,
                  ),
                  trailing: IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: _isUploading ? null : () => _removeFile(index),
                    color: theme.colorScheme.error,
                  ),
                );
              },
            ),
          ),
        ],
      ],
    );
  }

  String _formatFileSize(int? bytes) {
    if (bytes == null) return 'N/A';
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
  }
}

class _UploadedFileInfo {
  final String id;
  final String filename;
  final int? size;

  _UploadedFileInfo({
    required this.id,
    required this.filename,
    this.size,
  });
}

