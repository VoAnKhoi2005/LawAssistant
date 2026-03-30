import 'package:file_selector/file_selector.dart';
import 'package:flutter/material.dart';
import 'package:law_assistant_kg/src/core/api/models/document_models.dart';
import 'package:law_assistant_kg/src/core/api/services/document_api_service.dart';
import 'package:law_assistant_kg/src/core/api/services/upload_file_api_service.dart';

class DocumentUploadDialog extends StatefulWidget {
  const DocumentUploadDialog({
    super.key,
    required this.documentApiService,
    required this.uploadFileApiService,
  });

  final DocumentApiService documentApiService;
  final UploadFileApiService uploadFileApiService;

  @override
  State<DocumentUploadDialog> createState() => _DocumentUploadDialogState();
}

class _UploadedFileItem {
  _UploadedFileItem({required this.id, required this.name});

  final String id;
  final String name;
}

class _DocumentUploadDialogState extends State<DocumentUploadDialog> {
  final _formKey = GlobalKey<FormState>();
  final _soHieuController = TextEditingController();
  final _titleController = TextEditingController();
  final _effectiveDateController = TextEditingController();

  DateTime? _effectiveDate;
  bool _uploading = false;
  bool _submitting = false;
  final List<_UploadedFileItem> _files = [];

  @override
  void dispose() {
    _soHieuController.dispose();
    _titleController.dispose();
    _effectiveDateController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return AlertDialog(
      title: const Text('Add Document'),
      insetPadding: const EdgeInsets.symmetric(horizontal: 72, vertical: 48),
      content: ConstrainedBox(
        constraints: const BoxConstraints(
          minWidth: 760,
          maxWidth: 980,
        ),
        child: SingleChildScrollView(
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                TextFormField(
                  controller: _soHieuController,
                  decoration: const InputDecoration(
                    labelText: 'Số hiệu',
                    hintText: 'e.g. 15/2023/QH15',
                  ),
                  validator: (value) =>
                      value == null || value.isEmpty ? 'Required' : null,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _titleController,
                  decoration: const InputDecoration(
                    labelText: 'Title',
                    hintText: 'Document title',
                  ),
                  validator: (value) =>
                      value == null || value.isEmpty ? 'Required' : null,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _effectiveDateController,
                  readOnly: true,
                  decoration: InputDecoration(
                    labelText: 'Effective date',
                    suffixIcon: IconButton(
                      icon: const Icon(Icons.calendar_today),
                      onPressed: _pickDate,
                    ),
                  ),
                  validator: (_) =>
                      _effectiveDate == null ? 'Select a date' : null,
                  onTap: _pickDate,
                ),
                const SizedBox(height: 20),
                Text(
                  'Source files',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    OutlinedButton.icon(
                      onPressed: _uploading ? null : _pickAndUpload,
                      icon: const Icon(Icons.file_upload),
                      label: Text(_uploading ? 'Uploading...' : 'Pick & upload'),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      'Reorder to set processing order',
                      style: TextStyle(
                        color: colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                if (_files.isEmpty)
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: colorScheme.surfaceContainerLow,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: colorScheme.outlineVariant),
                    ),
                    child: Text(
                      'No files uploaded yet. Upload a document to proceed.',
                      style: TextStyle(
                        color: colorScheme.onSurfaceVariant,
                        fontSize: 13,
                      ),
                    ),
                  )
                else
                  SizedBox(
                    height: 220,
                    child: ReorderableListView.builder(
                      shrinkWrap: true,
                      buildDefaultDragHandles: false,
                      itemCount: _files.length,
                      onReorder: _reorderFiles,
                      itemBuilder: (context, index) {
                        final file = _files[index];
                        return ListTile(
                          key: ValueKey(file.id),
                          tileColor: colorScheme.surfaceContainerLow,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          leading: ReorderableDragStartListener(
                            index: index,
                            child: const Icon(Icons.drag_indicator),
                          ),
                          title: Text(file.name),
                          trailing: IconButton(
                            icon: const Icon(Icons.close),
                            onPressed: () => _removeFile(file),
                          ),
                        );
                      },
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: _submitting ? null : () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        FilledButton(
          onPressed: _submitting ? null : _submit,
          child: _submitting
              ? const SizedBox(
                  height: 18,
                  width: 18,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Create'),
        ),
      ],
    );
  }

  Future<void> _pickDate() async {
    final now = DateTime.now();
    final selected = await showDatePicker(
      context: context,
      initialDate: _effectiveDate ?? now,
      firstDate: DateTime(1950),
      lastDate: DateTime(now.year + 10),
    );
    if (selected != null) {
      setState(() {
        _effectiveDate = selected;
        _effectiveDateController.text =
            '${selected.day.toString().padLeft(2, '0')}/${selected.month.toString().padLeft(2, '0')}/${selected.year}';
      });
    }
  }

  Future<void> _pickAndUpload() async {
    final file = await openFile(
      acceptedTypeGroups: [
        const XTypeGroup(
          label: 'Documents',
          extensions: ['pdf', 'doc', 'docx'],
        ),
      ],
    );

    if (file == null) {
      return;
    }

    setState(() {
      _uploading = true;
    });

    final response =
        await widget.uploadFileApiService.uploadFile(file.path, file.name);

    if (!mounted) return;

    setState(() {
      _uploading = false;
    });

    final uploaded = response.data;
    if (!response.success || uploaded?.id == null) {
      _showError(response.error ?? 'Failed to upload file');
      return;
    }

    final fileId = uploaded!.id!.value;

    setState(() {
      _files.add(_UploadedFileItem(id: fileId, name: uploaded.filename));
    });
  }

  void _removeFile(_UploadedFileItem file) {
    setState(() {
      _files.remove(file);
    });
  }

  void _reorderFiles(int oldIndex, int newIndex) {
    if (newIndex > oldIndex) {
      newIndex -= 1;
    }
    setState(() {
      final item = _files.removeAt(oldIndex);
      _files.insert(newIndex, item);
    });
  }

  Future<void> _submit() async {
    if (_files.isEmpty) {
      _showError('Please upload at least one file.');
      return;
    }

    final valid = _formKey.currentState?.validate() ?? false;
    if (!valid || _effectiveDate == null) {
      return;
    }

    setState(() {
      _submitting = true;
    });

    final request = CreateDocumentRequest(
      soHieu: _soHieuController.text.trim(),
      title: _titleController.text.trim(),
      effectiveDate: _effectiveDate!.toIso8601String(),
      fileIds: _files.map((file) => file.id).toList(),
    );

    final response = await widget.documentApiService.createDocument(request);

    if (!mounted) return;

    setState(() {
      _submitting = false;
    });

    if (!response.success || response.data == null) {
      _showError(response.error ?? 'Failed to create document');
      return;
    }

    Navigator.of(context).pop(response.data);
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
}
