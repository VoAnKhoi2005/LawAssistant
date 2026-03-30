import 'common_models.dart';

class DocumentDto {
  final ObjectIdModel? id;
  final DateModel effectiveDate;
  final bool isActive;
  final String soHieu;
  final List<FileRef> sourceFiles;
  final String title;
  final List<FileRef>? files;
  final String? status;
  final String? taskId;
  final int? order;
  final String? error;

  const DocumentDto({
    this.id,
    required this.effectiveDate,
    required this.isActive,
    required this.soHieu,
    required this.sourceFiles,
    required this.title,
    this.files,
    this.status,
    this.taskId,
    this.order,
    this.error,
  });

  // Convenience getters for UI
  DateTime? get ngayHieuLuc => effectiveDate.value;
  String? get linhVuc => null; // TODO: Add to backend model if needed
  String? get trangThai => isActive ? 'Đang có hiệu lực' : 'Hết hiệu lực';

  factory DocumentDto.fromJson(Map<String, dynamic> json) {
    return DocumentDto(
      id: ObjectIdModel.maybeFromJson(json['_id'] ?? json['id']),
      effectiveDate: DateModel.fromJson(json['effective_date']),
      isActive: json['is_active'] as bool? ?? false,
      soHieu: json['so_hieu'] as String? ?? '',
      sourceFiles: FileRef.listFromJson(json['source_files']),
      title: json['title'] as String? ?? '',
      files: json['files'] != null ? FileRef.listFromJson(json['files']) : null,
      status: json['status'] as String?,
      taskId: json['task_id'] as String?,
      order: (json['order'] as num?)?.toInt(),
      error: json['error'] as String?,
    );
  }

  Map<String, dynamic> toJson({bool includeId = false}) {
    final map = <String, dynamic>{
      'effective_date': effectiveDate.toJson(),
      'is_active': isActive,
      'so_hieu': soHieu,
      'source_files': sourceFiles.map((file) => file.toJson()).toList(),
      'title': title,
      'files': files?.map((file) => file.toJson()).toList(),
      'status': status,
      'task_id': taskId,
      'order': order,
      'error': error,
    };
    if (includeId && id != null) {
      map['_id'] = id!.toJson();
    }
    map.removeWhere((key, value) => value == null);
    return map;
  }
}

class CreateDocumentRequest {
  final String soHieu;
  final String title;
  final String effectiveDate;
  final List<String> fileIds;

  const CreateDocumentRequest({
    required this.soHieu,
    required this.title,
    required this.effectiveDate,
    required this.fileIds,
  });

  Map<String, dynamic> toJson() => {
    'so_hieu': soHieu,
    'title': title,
    'effective_date': effectiveDate,
    'file_ids': fileIds,
  };
}

class UpdateDocumentRequest {
  final DateModel? effectiveDate;
  final bool? isActive;
  final String? soHieu;
  final List<String>? sourceFiles;
  final String? title;

  const UpdateDocumentRequest({
    this.effectiveDate,
    this.isActive,
    this.soHieu,
    this.sourceFiles,
    this.title,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{
      'effective_date': effectiveDate?.toJson(),
      'is_active': isActive,
      'so_hieu': soHieu,
      'source_files': sourceFiles,
      'title': title,
    };
    map.removeWhere((key, value) => value == null);
    return map;
  }
}
